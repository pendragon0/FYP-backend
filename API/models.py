from django.db import models
from django.contrib.auth.models import User

class UserReport(models.Model):
    email = models.EmailField()
    uploaded_file = models.FileField(upload_to='user_reports/', blank=True, null=True)
    diagnosis_file = models.FileField(upload_to='user_reports/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    report_identifier = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.email} - {self.uploaded_file.name} - {self.diagnosis_file.name}'

    @property
    def file_url(self):
        if self.uploaded_file and hasattr(self.uploaded_file, 'url'):
            return self.uploaded_file.url
        elif self.diagnosis_file and hasattr(self.diagnosis_file, 'url'):
            return self.diagnosis_file.url
        else:
            return None
