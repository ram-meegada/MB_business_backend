from django.db import models
from django.conf import settings


class OpenAIUsage(models.Model):
    FEATURE_CHOICES = [
        ('skills_extraction', 'Skills Extraction'),
    ]

    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES)
    model = models.CharField(max_length=50, default=settings.OPENAI_MODEL)
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField(null=True, blank=True)
    cost = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_cost(self):
        charges = settings.CHARGES.get(self.model, {})
        input_cost = (self.input_tokens/1_000_000) * charges.get('input_tokens', 0)
        output_cost = (self.output_tokens/1_000_000) * charges.get('output_tokens', 0)
        return input_cost + output_cost
