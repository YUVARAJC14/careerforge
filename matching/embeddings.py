from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    """Load the model once and reuse it (loading is slow, ~1-2s)."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_text(text: str):
    """Return a 384-dim embedding vector for the given text."""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()