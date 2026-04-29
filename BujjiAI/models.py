from django.db import models
from django.conf import settings


class LLMUsage(models.Model):
    SKILLS_EXTRACTION = 1
    CHAT = 2

    REQUEST_CHOICES = [
        (SKILLS_EXTRACTION, "Skills Extraction"),
        (CHAT, "Chat"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    model = models.CharField(verbose_name="Model", max_length=50)

    prompt_tokens = models.IntegerField(verbose_name="Prompt Tokens", default=0)
    completion_tokens = models.IntegerField(verbose_name="Completion Tokens", default=0)
    total_tokens = models.IntegerField(verbose_name="Total Tokens", default=0)
    cached_tokens = models.IntegerField(verbose_name="Cached Tokens", default=0)
    cost = models.FloatField(verbose_name="Cost (USD)")

    request_type = models.IntegerField(verbose_name="Request Type", choices=REQUEST_CHOICES)

    latency_ms = models.IntegerField(verbose_name="Latency (ms)", null=True, blank=True)

    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
