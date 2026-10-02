from django.contrib import admin
from .models import InterviewSession, InterviewQuestion

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title_snapshot', 'created_at', 'completed')

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('session', 'order', 'question_text')