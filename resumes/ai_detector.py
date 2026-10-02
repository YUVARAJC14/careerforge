from google import genai
from django.conf import settings
import json
import re

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

def analyze_resume_text(text):
    client = _get_client()
    prompt = f"""You are an AI-content detector analyzing a resume for signs of being
AI-generated versus genuinely human-written.

Resume text:
{text[:6000]}

Rate how likely this resume was AI-generated, from 0 (clearly human — natural, specific,
technical) to 100 (clearly AI-generated — generic corporate language, buzzwords).
Also list up to 5 specific sentences that sound most AI-generated, if any (empty list if none stand out).

Return ONLY valid JSON, no other text:
{{"score": <number>, "flagged_sentences": ["sentence1", "sentence2"]}}
"""
    response = client.models.generate_content(model='gemini-3.5-flash-lite', contents=prompt)
    result = _extract_json(response.text)
    return float(result.get('score', 0)), result.get('flagged_sentences', [])