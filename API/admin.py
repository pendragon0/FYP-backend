# ocr_app/admin.py

from django.contrib import admin
from .models import UserReport

class UserReportAdmin(admin.ModelAdmin):
    list_display = ('email', 'file_link', 'uploaded_at')
    search_fields = ('email', 'file')
    list_filter = ('uploaded_at',)

    def file_link(self, obj):
        if obj.file_url:
            return f'<a href="{obj.file_url}" target="_blank">{obj.file.name}</a>'
        else:
            return 'No file'
    file_link.allow_tags = True
    file_link.short_description = 'File'

admin.site.register(UserReport, UserReportAdmin)
