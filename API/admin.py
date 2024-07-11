from django.contrib import admin
from .models import UserReport

class UserReportAdmin(admin.ModelAdmin):
    list_display = ('email', 'uploaded_file', 'diagnosis_file', 'uploaded_at')
    search_fields = ('email', 'uploaded_file', 'diagnosis_file')
    list_filter = ('uploaded_at',)

    def uploaded_file_link(self, obj):
        if obj.uploaded_file_url:
            return f'<a href="{obj.uploaded_file_url}" target="_blank">{obj.uploaded_file.name}</a>'
        else:
            return 'No file'
    uploaded_file_link.allow_tags = True
    uploaded_file_link.short_description = 'Uploaded File'

    def diagnosis_file_link(self, obj):
        if obj.diagnosis_file_url:
            return f'<a href="{obj.diagnosis_file_url}" target="_blank">{obj.diagnosis_file.name}</a>'
        else:
            return 'No diagnosis file'
    diagnosis_file_link.allow_tags = True
    diagnosis_file_link.short_description = 'Diagnosis File'

admin.site.register(UserReport, UserReportAdmin)
