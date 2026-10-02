from django.db import models
from django.conf import settings
from pgvector.django import VectorField

class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True)
    embedding = VectorField(dimensions=384, null=True, blank=True)  # 384 = all-MiniLM-L6-v2 output size
    ai_content_score = models.FloatField(null=True, blank=True)  # for the AI-content checker, later
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s resume ({self.uploaded_at.date()})"