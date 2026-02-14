import os
import psycopg
import uuid

from contextlib import contextmanager
from psycopg.rows import dict_row
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()

CONNECTION_STRING = os.getenv("SUPABASE_CONNECTION_STRING")

@contextmanager
def get_connection():
    conn = psycopg.connect(CONNECTION_STRING)

    try:
        yield conn
    finally:
        conn.close()

def insert_job(
    job_id: str,
    filename: str,
    storage_path: str,
    user_id: str | None = None,
) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.pdfjob (
                    id,
                    user_id,
                    filename,
                    storage_path
                )
                VALUES (%s, %s, %s, %s)
                """,
                (job_id, user_id, filename, storage_path),
            )
        conn.commit()

    return job_id

def update_status(
    job_id: str,
    status: str,
    error_message: str | None = None,
    total_topics: int | None = None,
) -> None:

    fields = ["status = %s", "updated_at = now()"]
    values = [status]

    if error_message is not None:
        fields.append("error_message = %s")
        values.append(error_message)

    if total_topics is not None:
        fields.append("total_topics = %s")
        values.append(total_topics)

    values.append(job_id)

    query = f"""
        UPDATE public.pdfjob
        SET {", ".join(fields)}
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
        conn.commit()

def get_job(job_id: str) -> dict | None:
    query = """
        SELECT
            id,
            user_id,
            filename,
            storage_path,
            status,
            total_topics,
            completed_topics,
            error_message,
            created_at,
            updated_at
        FROM public.pdfjob
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (job_id,))
            result = cur.fetchone()

    return result

def insert_topics(pdf_id: str, topics: list[str]) -> None:
    query = """
        INSERT INTO public.pdftopics (id, pdf_id, topic_name, status)
        VALUES (%s, %s, %s, 'pending');
    """
    topic_ids = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            for topic in topics:
                topic_id = str(uuid.uuid4())
                cur.execute(query, (topic_id, pdf_id, topic))
                topic_ids.append(topic_id)
        conn.commit()
    
    return topic_ids

def insert_mcqs(pdf_id: str, topic_id: str, mcqs: list[dict]) -> str:
    query = """
        INSERT INTO public.mcqs (id, pdf_id, topic_id, mcq_data)
        VALUES (%s, %s, %s, %s);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            mcq_id = str(uuid.uuid4())
            cur.execute(
                query,
                (
                    mcq_id,
                    pdf_id,
                    topic_id,
                    Jsonb(mcqs), 
                ),
            )
            
        conn.commit()
    return mcq_id

def update_topic_status(topic_id: str, pdf_id: str, status: str) -> None:
    query = """
        UPDATE public.pdftopics
        SET status = %s, updated_at = now()
        WHERE id = %s AND pdf_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (status, topic_id, pdf_id))
        conn.commit()

def increment_completed_topics(pdf_id: str) -> None:
    query = """
        UPDATE public.pdfjob
        SET
            completed_topics = (
                SELECT COUNT(*)
                FROM public.pdftopics
                WHERE pdf_id = %s
                AND status = 'completed'
            ),
            updated_at = now()
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (pdf_id, pdf_id))
        conn.commit()    

def get_all_jobs() -> list[dict]:
    query = """
        SELECT
            id,
            user_id,
            filename,
            status,
            total_topics,
            completed_topics,
            error_message,
            created_at,
            updated_at
        FROM public.pdfjob
        ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query)
            return cur.fetchall()
        
def get_jobs_by_user(user_id: str) -> list[dict]:
    query = """
        SELECT
            id,
            user_id,
            filename,
            status,
            total_topics,
            completed_topics,
            error_message,
            created_at,
            updated_at
        FROM public.pdfjob
        WHERE user_id = %s
        ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()

def get_topics_by_pdf(pdf_id: str) -> list[dict]:
    query = """
        SELECT
            id,
            topic_name,
            status,
            created_at,
            updated_at
        FROM public.pdftopics
        WHERE pdf_id = %s
        ORDER BY created_at ASC;
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (pdf_id,))
            return cur.fetchall()

def get_mcqs_by_topic(topic_id: str) -> dict | None:
    query = """
        SELECT
            id,
            topic_id,
            mcq_data,
            created_at
        FROM public.mcqs
        WHERE topic_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (topic_id,))
            return cur.fetchone()

def delete_job(job_id: str) -> None:
    query = "DELETE FROM public.pdfjob WHERE id = %s;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (job_id,))
        conn.commit()
        
def reset_job(job_id: str) -> None:
    query = """
        UPDATE public.pdfjob
        SET
            status = 'pending',
            total_topics = 0,
            completed_topics = 0,
            error_message = NULL,
            updated_at = now()
        WHERE id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (job_id,))
        conn.commit()