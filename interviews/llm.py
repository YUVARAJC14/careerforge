from google import genai
from django.conf import settings
import json
import re
import time

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _extract_json(text):
    text = text.strip()
    text = re.sub(r'^```json\s*|\s*```$', '', text)
    return json.loads(text)


def generate_hr_questions(job_title, job_description, num_questions=5):
    client = _get_client()
    prompt = f"""You are an experienced HR interviewer preparing questions for a candidate
applying to this role:

Job Title: {job_title}
Job Description: {job_description[:1500]}

Generate {num_questions} realistic HR/behavioral interview questions for this role.
Order them from easiest to hardest: start with 1-2 warm-up questions (background,
motivation, why this role), then move into behavioral questions (teamwork, challenges),
and end with 1-2 more specific role/technical questions based on the job description.

Return ONLY a JSON array of strings, no other text. Example format:
["question 1", "question 2", "question 3"]
"""
    response = _generate_with_retry(prompt)
    return _extract_json(response.text)


def generate_expected_answer(question, job_title, job_description):
    client = _get_client()
    prompt = f"""You are an expert career coach. A candidate is interviewing for this role:

Job Title: {job_title}
Job Description: {job_description[:1000]}

Interview Question: {question}

Write a strong, realistic model answer (3-5 sentences) that a well-prepared candidate
might give. Be specific and natural, not generic corporate language.

Return ONLY the answer text, no other formatting or preamble.
"""
    response = _generate_with_retry(prompt)
    return response.text.strip()


FILLER_WORDS = ['um', 'uh', 'umm', 'uhh', 'like', 'you know', 'basically', 'actually', 'literally']

def count_filler_words(transcript):
    text = transcript.lower()
    return sum(text.count(f) for f in FILLER_WORDS)


def generate_voice_feedback(question, transcript, job_title, job_description, wpm, filler_count):
    client = _get_client()
    prompt = f"""You are a warm, encouraging interview coach giving real-time spoken feedback.

Job Title: {job_title}
Interview Question: {question}
Candidate's spoken answer (transcribed): {transcript}
Speaking pace: {wpm:.0f} words per minute
Filler words used: {filler_count}

In 1-2 short sentences, give brief, natural-sounding spoken feedback on their COMMUNICATION
(pace, clarity, filler words if notable) — NOT on whether the answer's content was correct.
Sound like a coach speaking out loud, encouraging and conversational. No bullet points.
"""
    response = _generate_with_retry(prompt)
    return response.text.strip()

def generate_greeting(job_title):
    client = _get_client()
    prompt = f"""You are a warm, professional HR interviewer about to start a mock interview
for a candidate applying to a {job_title} role.

Write a short, natural spoken greeting (2-3 sentences) to open the interview: welcome them,
briefly mention you'll ask a few questions starting easy and getting more specific, and
tell them to answer naturally out loud. Sound like a real person talking, not a script.

Return ONLY the greeting text, no formatting.
"""
    response = _generate_with_retry(prompt)
    return response.text.strip()

def _generate_with_retry(prompt, max_retries=3):
    client = _get_client()
    last_error = None
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model='gemini-3.5-flash-lite', contents=prompt)
        except Exception as e:
            last_error = e
            if '503' in str(e) or 'UNAVAILABLE' in str(e):
                wait = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait)
                continue
            raise  # don't retry on errors that aren't transient
    raise last_error