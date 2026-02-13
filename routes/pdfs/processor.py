from fastapi import APIRouter 
from fastapi import UploadFile, File
from fastapi import HTTPException, status

from supabase.bucket import upload_pdf
from supabase.postgresdb import insert_job

import uuid 

router = APIRouter(prefix="/pdfs")

@router.post("/upload") 
async def upload_pdfs(files: list[UploadFile] = File(...)):
    jobs : list = []
    print("Received files:", [file.content_type for file in files])

    for file in files: 
        if file.content_type != "application/pdf":
            continue 
        try: 
            pdf_id : str = str(uuid.uuid4())
            pdf_bytes: bytes = await file.read()

            storage_key : str = upload_pdf(pdf_id, pdf_bytes)
            job_id = insert_job(pdf_id, file.filename, storage_key)
            jobs.append(job_id)

        except Exception as err: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error uploading {file.filename}: {str(err)}"
            )
        
    return {"job_ids": jobs, "length": len(jobs)}


        
        


