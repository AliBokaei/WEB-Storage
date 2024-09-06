from django.db import models
from django.contrib.auth.models import User


class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_link = models.URLField(max_length=500)
    file_type = models.CharField(max_length=100, blank=True)
    size = models.IntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)

    def __str__(self):
        return f"{self.file_name} uploaded by {self.uploaded_by}"


class FileShare(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_shares')
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.title} shared with {self.user.username}"
