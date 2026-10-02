import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from jobs.models import JobPosting
from .models import InterviewSession, InterviewQuestion
from .llm import generate_hr_questions, generate_expected_answer, generate_voice_feedback, count_filler_words, generate_greeting
import requests as ext_requests
from django.conf import settings
from django.utils import timezone
from django.contrib import messages

DAILY_INTERVIEW_LIMIT = 6

def _interviews_today(user):
    today = timezone.now().date()
    return InterviewSession.objects.filter(user=user, created_at__date=today).count()

@login_required
def start_interview(request, job_id):
    if _interviews_today(request.user) >= DAILY_INTERVIEW_LIMIT:
        messages.error(request, f"You've hit today's limit of {DAILY_INTERVIEW_LIMIT} mock interviews. Come back tomorrow!")
        return redirect('job_matches')

    job = get_object_or_404(JobPosting, id=job_id)

    session = InterviewSession.objects.create(
        user=request.user,
        job=job,
        job_title_snapshot=job.title,
    )

    questions = generate_hr_questions(job.title, job.description)
    for i, q_text in enumerate(questions, start=1):
        InterviewQuestion.objects.create(session=session, order=i, question_text=q_text)

    return redirect('take_interview', session_id=session.id)


@login_required
def take_interview(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = session.questions.all()
    return render(request, 'interviews/take.html', {'session': session, 'questions': questions})


@require_POST
@login_required
def submit_interview(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

    for question in session.questions.all():
        answer = request.POST.get(f'answer_{question.id}', '').strip()
        question.user_answer = answer
        question.expected_answer = generate_expected_answer(
            question.question_text, session.job_title_snapshot,
            session.job.description if session.job else ''
        )
        question.save()

    session.completed = True
    session.save()
    return redirect('interview_results', session_id=session.id)


@login_required
def interview_results(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    return render(request, 'interviews/results.html', {'session': session})


@login_required
def start_voice_interview(request, job_id):
    if _interviews_today(request.user) >= DAILY_INTERVIEW_LIMIT:
        messages.error(request, f"You've hit today's limit of {DAILY_INTERVIEW_LIMIT} mock interviews. Come back tomorrow!")
        return redirect('job_matches')

    job = get_object_or_404(JobPosting, id=job_id)
    session = InterviewSession.objects.create(user=request.user, job=job, job_title_snapshot=job.title)
    questions = generate_hr_questions(job.title, job.description)
    for i, q_text in enumerate(questions, start=1):
        InterviewQuestion.objects.create(session=session, order=i, question_text=q_text)
    return redirect('voice_interview', session_id=session.id)


@login_required
def voice_interview(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = list(session.questions.values('id', 'question_text', 'order'))
    return render(request, 'interviews/voice.html', {
        'session': session,
        'questions_json': json.dumps(questions),
    })


@require_POST
@login_required
def voice_answer(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    data = json.loads(request.body)
    question = get_object_or_404(InterviewQuestion, id=data.get('question_id'), session=session)

    transcript = data.get('transcript', '').strip()
    duration = float(data.get('duration_seconds', 0) or 0)
    word_count = len(transcript.split())
    wpm = (word_count / duration * 60) if duration > 0 else 0
    filler_count = count_filler_words(transcript)

    question.user_answer = transcript
    question.words_per_minute = round(wpm, 1)
    question.filler_word_count = filler_count
    question.expected_answer = generate_expected_answer(
        question.question_text, session.job_title_snapshot,
        session.job.description if session.job else ''
    )
    question.communication_tip = generate_voice_feedback(
        question.question_text, transcript, session.job_title_snapshot,
        session.job.description if session.job else '', wpm, filler_count
    )
    question.save()
    return JsonResponse({'tip': question.communication_tip})


@require_POST
@login_required
def finish_voice_interview(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    session.completed = True
    session.save()
    return JsonResponse({'ok': True})

@login_required
def voice_interview(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = list(session.questions.values('id', 'question_text', 'order'))
    greeting = generate_greeting(session.job_title_snapshot)
    return render(request, 'interviews/voice.html', {
        'session': session,
        'questions_json': json.dumps(questions),
        'greeting': greeting,
    })

@login_required
def tts_speak(request):
    text = request.GET.get('text', '')
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = ext_requests.post(url, json=payload, headers=headers, timeout=20)
    return HttpResponse(response.content, content_type="audio/mpeg")