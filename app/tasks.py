from app.celery_app import celery_app as job 
from llm.client import LLMClient
from llm.prompts.store import PromptStore
from utils.extractors import extract_list 

@job.task(name="extract_topics", bind = True)
def extract_topics(self, client: LLMClient, pdf_bytes: bytes) -> list: 
    try: 
        response = client.generate_with_pdfs(
            prompt=PromptStore.topic_extraction.get(),
            pdfs=[pdf_bytes],
        )

        topics = extract_list(response)
        
    except Exception as err: 
        pass 

    


