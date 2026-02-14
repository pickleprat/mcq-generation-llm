from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.tasks import queue_job

import supabase.bucket as sb_bucket
import supabase.postgresdb as sb_db
import traceback
import uuid

router = APIRouter(prefix="/pdfs", tags=["PDF Jobs"])

@router.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    jobs: list = []

    for file in files:
        if file.content_type != "application/pdf":
            continue

        try:
            pdf_id: str = str(uuid.uuid4())
            pdf_bytes: bytes = await file.read()

            storage_key: str = sb_bucket.upload_pdf(pdf_id, pdf_bytes)

            job_id: str = sb_db.insert_job(
                pdf_id=pdf_id,
                filename=file.filename,
                storage_path=storage_key,
            )

            queue_job.delay(pdf_id)

            jobs.append(job_id)

        except Exception as err:
            tb = traceback.format_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "file": file.filename,
                    "error_type": str(type(err)),
                    "error_message": str(err),
                    "traceback": tb,
                },
            )

    return {"job_ids": jobs}

@router.get("/{job_id}")
def get_job(job_id: str):
    job = sb_db.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    progress = 0
    if job["total_topics"] and job["total_topics"] > 0:
        progress = round(
            (job["completed_topics"] / job["total_topics"]) * 100, 2
        )

    return {
        "job_id": job["id"],
        "filename": job["filename"],
        "status": job["status"],
        "progress_percent": progress,
        "total_topics": job["total_topics"],
        "completed_topics": job["completed_topics"],
        "error_message": job["error_message"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }

@router.get("/{job_id}/topics")
def get_topics(job_id: str):
    job = sb_db.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    topics = sb_db.get_topics_by_pdf(job_id)

    return {
        "job_id": job_id,
        "status": job["status"],
        "topics": topics,
    }

@router.get("/{job_id}/topics/{topic_id}/mcqs")
def get_mcqs(job_id: str, topic_id: str):
    job = sb_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    mcqs = sb_db.get_mcqs_by_topic(topic_id)

    if not mcqs:
        raise HTTPException(status_code=404, detail="MCQs not found")

    return {
        "job_id": job_id,
        "topic_id": topic_id,
        "mcqs": mcqs,
    }

@router.get("/")
def list_jobs(user_id: str | None = None):
    if user_id:
        jobs = sb_db.get_jobs_by_user(user_id)
    else:
        jobs = sb_db.get_all_jobs()

    return {"jobs": jobs}
        
        


