from django.contrib import admin
from .models import UploadedFile


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_link', 'file_type', 'size', 'upload_date', 'uploaded_by')
    search_fields = ('file_name', 'uploaded_by__username')
    list_filter = ('upload_date', 'file_type', 'uploaded_by')


admin.site.register(UploadedFile, UploadedFileAdmin)


class FileShareAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'shared_at')
    search_fields = ('file__title', 'user__username')
