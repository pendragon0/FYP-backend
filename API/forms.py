# ocr_app/forms.py

from django import forms
from .models import UserReport

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ['file']
