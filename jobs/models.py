from django.db import models
from pgvector.django import VectorField

class JobPosting(models.Model):
    SOURCE_CHOICES = [
        ('jsearch', 'JSearch (LinkedIn/Indeed/Glassdoor)'),
        ('adzuna', 'Adzuna'),
        ('internshala', 'Internshala'),
        ('manual', 'Manual entry'),
    ]

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_url = models.URLField(max_length=500)
    embedding = VectorField(dimensions=384, null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.company}"