from app.celery_app import celery_app as job
from llm.client import LLMClient
from llm.prompts.store import PromptStore
from utils.extractors import extract_list, extract_json
from dotenv import load_dotenv
from celery import chord
from jinja2 import Template
import os

import supabase.bucket as sb_bucket
import supabase.postgresdb as sb_db

load_dotenv()

GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")


# -----------------------------
# Finalize Job
# -----------------------------

@job.task(bind=True)
def finalize_job(self, results, pdf_id: str):
    """
    Called only after all generate_mcq tasks succeed.
    """
    sb_db.update_status(pdf_id, "completed")


# -----------------------------
# Generate MCQs Per Topic
# -----------------------------

@job.task(bind=True, max_retries=3)
def generate_mcq(self, pdf_id: str, topic: str, topic_id: str):
    try:
        sb_db.update_topic_status(topic_id, pdf_id, "processing")

        client = LLMClient(client="gemini", api_key=GEMINI_API_KEY)

        prompt_template = Template(PromptStore.mcq_generation.get())
        query = prompt_template.render(
            topic=topic,
            count=10,
            start_index=1,
        )

        job_data = sb_db.get_job(pdf_id)
        pdf_bytes = sb_bucket.download_pdf(job_data["storage_path"])

        response = client.generate_with_pdfs(
            prompt=query,
            pdfs=[pdf_bytes],
        )

        print("Gemini response for topic:", topic)
        print("Response:", response)

        mcqs = extract_json(response)

        mcq_id = sb_db.insert_mcqs(pdf_id, topic_id, mcqs)

        sb_db.update_topic_status(topic_id, pdf_id, "completed")
        sb_db.increment_completed_topics(pdf_id)

        return {"topic": topic, "mcq_id": mcq_id}

    except Exception as err:
        # If retries still available → retry
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries  # exponential backoff
            print(f"Retrying topic {topic} in {countdown} seconds...")
            raise self.retry(exc=err, countdown=countdown)

        # Retries exhausted → mark topic failed
        sb_db.update_topic_status(topic_id, pdf_id, "failed")
        raise err


# -----------------------------
# Queue Job
# -----------------------------

@job.task(name="queue_job", bind=True)
def queue_job(self, pdf_id: str):
    try:
        sb_db.update_status(pdf_id, "generating topics")

        job_data = sb_db.get_job(pdf_id)
        if not job_data:
            raise ValueError(f"Job with PDF ID {pdf_id} not found.")

        pdf_bytes = sb_bucket.download_pdf(job_data["storage_path"])

        client = LLMClient(client="gemini", api_key=GEMINI_API_KEY)

        template = PromptStore.topic_extraction.get()
        response = client.generate_with_pdfs(
            prompt=template,
            pdfs=[pdf_bytes],
        )

        topics = extract_list(response)

        sb_db.update_status(
            pdf_id,
            "generating mcqs",
            total_topics=len(topics),
            error_message=None,
        )

        topic_ids = sb_db.insert_topics(pdf_id, topics)

        tasks = [
            generate_mcq.s(pdf_id, topic, topic_id)
            for topic, topic_id in zip(topics, topic_ids)
        ]

        chord(tasks)(finalize_job.s(pdf_id))

    except Exception as err:
        sb_db.update_status(pdf_id, "failed", error_message=str(err))