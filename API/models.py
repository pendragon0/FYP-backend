# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class UserReport(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # text = models.TextField(blank=True, null=True)
    email = models.EmailField()

    def __str__(self):
        return f'{self.email} - {self.file.name}'
    
    
    @property
    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        else:
            return None
