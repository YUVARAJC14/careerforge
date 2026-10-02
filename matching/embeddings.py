from google import genai
from google.genai import types
from django.conf import settings

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client

def embed_text(text: str):
    """Return a 384-dim embedding vector via Gemini's embedding API."""
    client = _get_client()
    result = client.models.embed_content(
        model='gemini-embedding-001',
        contents=text[:8000],
        config=types.EmbedContentConfig(output_dimensionality=384),
    )
    return result.embeddings[0].values