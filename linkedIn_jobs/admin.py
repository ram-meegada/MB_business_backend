from django.contrib import admin
from linkedIn_jobs.models import Job, JobRawData, Company, Skill, JobSkill


@admin.action(description="Approve selected skills")
def approve_selected_skills(modeladmin, request, queryset):
    queryset.update(is_approved=True)
    modeladmin.message_user(request, f"Selected skills are approved. Please add them to the canonical skills list if not already added.")

class SkillsAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_approved')
    search_fields = ('name',)
    ordering = ('name',)
    actions = [approve_selected_skills]

    def get_queryset(self, request):
        return Skill.allobjects.all()

class JobSkillAdmin(admin.ModelAdmin):
    list_display = ('job', 'skill_name')
    search_fields = ('job__title', 'skill__name')
    raw_id_fields = ('job', 'skill',)

    @admin.display()
    def skill_name(self, obj):
        return obj.skill.name


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'primary_tech', 'role_category', 'location', 'scraped_at')
    list_filter = ('location', 'role_category')
    search_fields = ('title', 'description', 'company__name')
    raw_id_fields = ('company',)


admin.site.register(Job, JobAdmin)
admin.site.register(JobRawData)
admin.site.register(Company)
admin.site.register(Skill, SkillsAdmin)
admin.site.register(JobSkill, JobSkillAdmin)
