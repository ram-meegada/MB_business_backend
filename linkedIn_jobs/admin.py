from django.contrib import admin
from linkedIn_jobs.models import Job, JobRawData, Company


admin.site.register(Job)
admin.site.register(JobRawData)
admin.site.register(Company)
