from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    slugname = models.CharField(max_length=255, unique=True)
    company_url = models.URLField()
    logo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class JobRawData(models.Model):
    raw_html = models.BinaryField()
    scraped_at = models.DateTimeField(auto_now_add=True)


class Job(models.Model):
    LINKEDIN = 'LinkedIn'

    SOURCE_CHOICES = [
        (LINKEDIN, 'LinkedIn'),
    ]

    job_id = models.BigIntegerField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.TextField()
    location = models.TextField(null=True)
    job_url = models.URLField(max_length=500)
    description = models.TextField(null=True)
    posted_at = models.DateTimeField(null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="linkedin")
    payload = models.JSONField()
    raw_data = models.ForeignKey(JobRawData, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
