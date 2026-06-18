from celery import shared_task
import time
from .models import TranslationJob, TranslationStates

@shared_task
def add(a, b):
    return a + b

@shared_task
def dummy_translate_job(job_id):
    time.sleep(3)
    job = TranslationJob.objects.get(id=job_id)
    job.status = TranslationStates.DONE
    job.save()