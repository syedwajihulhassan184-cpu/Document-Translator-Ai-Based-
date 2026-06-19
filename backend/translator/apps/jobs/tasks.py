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
    total_chunks = chunks.count()

    for chunk in chunks:
        try:
            result = translate_chunk(chunk.original_text, job.source_lang, job.target_lang)
            chunk.translated_text = result
            chunk.status = ChunkStatus.DONE
            chunk.save()
        except Exception:
            chunk.retry_count += 1
            if chunk.retry_count >= 3:
                chunk.status = ChunkStatus.FAILED
                job.failed_chunks += 1
                chunk.save()
            else:
                continue


    if job.failed_chunks / total_chunks <= 0.3:
        job.status = TranslationStates.DONE
    else:
        job.status = TranslationStates.FAILED

    job.completed_at = timezone.now()
    job.save()

    