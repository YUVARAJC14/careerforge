from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Resume
from .extraction import extract_text
from matching.embeddings import embed_text
from .ai_detector import analyze_resume_text
from django.utils import timezone

DAILY_RESUME_LIMIT = 5

def _resumes_today(user):
    today = timezone.now().date()
    return Resume.objects.filter(user=user, uploaded_at__date=today).count()

@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume_file'):
        resume = Resume.objects.create(
            user=request.user,
            file=request.FILES['resume_file'],
        )
        try:
            resume.raw_text = extract_text(resume.file)
            resume.embedding = embed_text(resume.raw_text)
            score, flagged = analyze_resume_text(resume.raw_text)
            resume.ai_content_score = score
            resume.save()
        except ValueError as e:
            resume.delete()
            return render(request, 'resumes/upload.html', {'error': str(e)})

        return redirect('resume_result', resume_id=resume.id)
    return render(request, 'resumes/upload.html')


@login_required
def resume_result(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    _, flagged_sentences = analyze_resume_text(resume.raw_text)
    return render(request, 'resumes/result.html', {
        'resume': resume,
        'flagged_sentences': flagged_sentences,
    })