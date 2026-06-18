from django.contrib import admin
from  .models import File
# Register your models here.

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'file_format', 'size_bytes', 'uploaded_at']
    list_filter = ['file_format', 'is_scanned_pdf']
    search_fields = ['original_filename', 'user__email']