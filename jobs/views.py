from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from pgvector.django import CosineDistance
from .models import JobPosting
from resumes.models import Resume

MAX_GOOD_DISTANCE = 0.6  # cosine distance above this = not a real match

@login_required
def job_matches(request):
    resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()

    if not resume or resume.embedding is None:
        return render(request, 'jobs/matches.html', {'no_resume': True})

    matches = (
        JobPosting.objects
        .annotate(distance=CosineDistance('embedding', resume.embedding))
        .order_by('distance')[:20]
    )

    good_matches = [m for m in matches if m.distance <= MAX_GOOD_DISTANCE]
    weak_signal = len(good_matches) == 0

    return render(request, 'jobs/matches.html', {
        'matches': good_matches if good_matches else matches[:5],
        'weak_signal': weak_signal,
        'resume': resume,
    })