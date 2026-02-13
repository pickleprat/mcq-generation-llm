from celery import Celery 
import ssl
import os 

redis_url = os.getenv("REDIS_URL")

celery_app = Celery(
    'MCQ-Generation', 
    broker = redis_url, 
    backend = redis_url  
)


celery_app.conf.update(
    broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
)

