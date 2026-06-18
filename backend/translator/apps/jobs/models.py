from django.db import models
from accounts.models import CustomUser
from files.models import File
# Create your models here.

class TranslationStates(models.TextChoices):
    PENDING = 'pending','Pending',
    PARSING = 'parsing', 'Parsing'
    TRANSLATING = 'translating','Translating'
    REBUILDING = 'rebuilding', 'Rebuilding'
    DONE = 'done', 'Done'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'

class TranslationJobManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter().exclude(
            status__in=[TranslationStates.DONE, TranslationStates.CANCELLED]
        )

class TranslationJob(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    input_file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=150, choices=TranslationStates.choices)
    source_lang = models.CharField(max_length=100)
    target_lang = models.CharField(max_length=100)
    total_pages = models.IntegerField(default=0)
    processed_pages = models.IntegerField(default=0)
    failed_chunks = models.IntegerField(default=0)
    error_message = models.CharField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    objects = models.Manager()
    active = TranslationJobManager()

class ChunkStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In_progress'
    DONE = 'done', 'Done'
    FAILED = 'failed', 'Failed'

class Chunk(models.Model):
    job = models.ForeignKey(TranslationJob, on_delete=models.CASCADE)
    chunk_index = models.IntegerField(default=0)
    page_start = models.IntegerField(default=1)
    page_end = models.IntegerField()
    original_text = models.TextField()
    translated_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=ChunkStatus.choices)
    retry_count = models.IntegerField(default=0)
    layout_metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
