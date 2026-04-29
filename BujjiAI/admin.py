from django.contrib import admin
from BujjiAI.models import LLMUsage


class LLMUsageAdmin(admin.ModelAdmin):
    list_display = ('get_request_type_display', 'prompt_tokens', 'completion_tokens', 'cached_tokens', 'total_tokens', 'cost', 'latency_ms', 'is_success', 'created_at')
    list_filter = ('model', 'request_type', 'is_success', 'created_at')
    search_fields = ('model', 'request_type')

    @admin.display(description="Request Type")
    def get_request_type_display(self, obj):
        return obj.get_request_type_display()


admin.site.register(LLMUsage, LLMUsageAdmin)
