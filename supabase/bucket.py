import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BUCKET_ENDPOINT = os.getenv("SUPABASE_BUCKET_ENDPOINT")
ACCESS_KEY = os.getenv("SUPABASE_BUCKET_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("SUPABASE_BUCKET_ACCESS_KEY")

BUCKET_NAME = "content" 

s3_client = boto3.client(
    "s3",
    endpoint_url=BUCKET_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


def upload_pdf(pdf_id: str, pdf_bytes: bytes) -> str:
    key = f"{pdf_id}.pdf"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=pdf_bytes,
        ContentType="application/pdf",
    )

    return key


def download_pdf(storage_key: str) -> bytes:
    response = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=storage_key,
    )

    return response["Body"].read()