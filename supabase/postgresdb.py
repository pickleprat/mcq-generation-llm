import os
import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv

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