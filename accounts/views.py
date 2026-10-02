from django.shortcuts import render
from django.utils import timezone
from resumes.models import Resume
from jobs.models import JobPosting
from interviews.models import InterviewSession

def home(request):
    context = {}
    if request.user.is_authenticated:
        latest_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
        today = timezone.now().date()
        interviews_today = InterviewSession.objects.filter(user=request.user, created_at__date=today).count()
        recent_interviews = InterviewSession.objects.filter(user=request.user).order_by('-created_at')[:3]
        total_jobs = JobPosting.objects.count()
        total_interviews = InterviewSession.objects.filter(user=request.user).count()

        context.update({
            'latest_resume': latest_resume,
            'interviews_today': interviews_today,
            'interview_limit': 6,
            'recent_interviews': recent_interviews,
            'total_jobs': total_jobs,
            'total_interviews': total_interviews,
        })
    return render(request, 'home.html', context)