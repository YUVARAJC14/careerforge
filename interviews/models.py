from django.db import models
from django.conf import settings
from jobs.models import JobPosting


class InterviewSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_sessions')
    job = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, blank=True)
    job_title_snapshot = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} — {self.job_title_snapshot} ({self.created_at.date()})"


class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    user_answer = models.TextField(blank=True)
    expected_answer = models.TextField(blank=True)
    communication_tip = models.TextField(blank=True)
    words_per_minute = models.FloatField(null=True, blank=True)
    filler_word_count = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"