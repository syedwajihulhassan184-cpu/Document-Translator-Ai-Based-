from django.db import models
from accounts.models import CustomUser
# Create your models here.

class FileFormat(models.TextChoices):
    PDF = 'pdf', 'Pdf'
    DOCX = 'docx', 'Docx'
    PPTX = 'pptx', 'Pptx'
    TXT = 'txt', 'Txt'

class File(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mime_type = models.CharField(max_length=100)
    file_format = models.CharField(max_length=100, choices=FileFormat.choices)
    page_count = models.IntegerField(null=True, blank=True)
    size_bytes = models.BigIntegerField()
    is_scanned_pdf = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    storage_key = models.CharField(max_length=500)
    original_filename = models.CharField(max_length=255)
    checksum_sha256  = models.CharField(max_length=64)

    def __str__(self):
        return self.original_filename