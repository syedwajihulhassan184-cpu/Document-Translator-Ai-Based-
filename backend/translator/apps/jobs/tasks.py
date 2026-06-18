from celery import shared_task
import time
from .models import Chunk, ChunkStatus,TranslationJob, TranslationStates
from core.translators.translator import translate_chunk
from django.utils import timezone

@shared_task
def translate_job(job_id):
    job = TranslationJob.objects.get(id=job_id)
    job.status = TranslationStates.TRANSLATING
    job.save()
    chunks = Chunk.objects.filter(job=job,status=ChunkStatus.PENDING)

    for chunk in chunks:
        result = translate_chunk(chunk.original_text, job.source_lang, job.target_lang)
        chunk.translated_text = result
        chunk.status = ChunkStatus.DONE
        chunk.save()

    job.status = TranslationStates.DONE
    job.completed_at = timezone.now()
    job.save()

    