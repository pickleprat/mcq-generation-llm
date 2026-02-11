from llm.client import LLMClient
from llm.prompts.store import PromptStore
from jinja2 import Template
from dotenv import load_dotenv

import os
import json
import random
import re


# -----------------------------
# Utility Functions
# -----------------------------

def extract_json_array(raw: str) -> str:
    """
    Extract the first JSON array found in the raw model output.
    """
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in model output.")
    return match.group(0)


REQUIRED_KEYS = {
    "mcq_number",
    "question",
    "options",
    "answer",
    "topics_covered",
    "reasoning",
}


def validate_mcqs(mcqs: list, expected_count: int):
    if not isinstance(mcqs, list):
        raise ValueError("MCQs output is not a list.")

    if len(mcqs) != expected_count:
        raise ValueError(
            f"Expected {expected_count} MCQs, got {len(mcqs)}."
        )

    for mcq in mcqs:
        if not REQUIRED_KEYS.issubset(mcq.keys()):
            raise ValueError("MCQ missing required fields.")


# -----------------------------
# Main Execution
# -----------------------------

load_dotenv()

GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

AWT_PDF: str = os.path.join("content", "awt.ppt.pdf")

if not os.path.exists(AWT_PDF):
    raise FileNotFoundError(f"PDF not found at: {AWT_PDF}")

with open(AWT_PDF, "rb") as f:
    pdf_bytes = f.read()

client = LLMClient(
    client="gemini",
    api_key=GEMINI_API_KEY,
    model="gemini-2.5-flash-lite",
)

# -----------------------------
# Step 1: Extract Topics
# -----------------------------

print("\n--- Extracting Topics ---\n")

topic_output = ""

for chunk in client.stream_with_pdfs(
    prompt=PromptStore.topic_extraction.get(),
    pdfs=[pdf_bytes],
):
    print(chunk, end="", flush=True)
    topic_output += chunk

print("\n\n--- Parsing Topics ---\n")

cleaned_topics_json = extract_json_array(topic_output)

topics = json.loads(cleaned_topics_json)

if not isinstance(topics, list) or len(topics) == 0:
    raise ValueError("Invalid or empty topic list extracted.")

print("Parsed topics:", topics)

# -----------------------------
# Step 2: Select Topics
# -----------------------------

random.seed(42)  # deterministic for debugging
selected_topics = random.sample(topics, min(3, len(topics)))

print("\n--- Selected Topics ---\n")
print(selected_topics)

# -----------------------------
# Step 3: Generate MCQs
# -----------------------------

mcq_template_str = PromptStore.mcq_generation.get()
template = Template(mcq_template_str)

all_mcqs = []
question_index = 1

for topic in selected_topics:
    print(f"\n\n--- Generating MCQs for Topic: {topic} ---\n")

    mcq_prompt = template.render(
        topics=topic,
        count=10,
        start_index=question_index,
    )

    topic_output = ""

    for chunk in client.stream_with_pdfs(
        prompt=mcq_prompt,
        pdfs=[pdf_bytes],
    ):
        print(chunk, end="", flush=True)
        topic_output += chunk

    print("\n\n--- Parsing MCQs ---\n")

    cleaned_mcq_json = extract_json_array(topic_output)

    parsed_mcqs = json.loads(cleaned_mcq_json)

    validate_mcqs(parsed_mcqs, expected_count=10)

    all_mcqs.extend(parsed_mcqs)

    question_index += 10

# -----------------------------
# Step 4: Save Output
# -----------------------------

output_path = os.path.join("content", "generated_mcqs.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_mcqs, f, indent=4)

print(f"\n\nSaved {len(all_mcqs)} MCQs to {output_path}")