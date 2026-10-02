import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import re

_model = None
_tokenizer = None

def _load():
    global _model, _tokenizer
    if _model is None:
        _tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
        _model = GPT2LMHeadModel.from_pretrained('gpt2')
        _model.eval()
    return _model, _tokenizer


def _sentence_perplexity(sentence, model, tokenizer):
    encodings = tokenizer(sentence, return_tensors='pt')
    input_ids = encodings.input_ids
    if input_ids.shape[1] < 2:
        return None
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
    return torch.exp(outputs.loss).item()


def _looks_like_heading(unit):
    """
    Detects titles/headings (project names, section labels) that aren't
    real prose and shouldn't be scored for AI-likeness. Real sentences mix
    capitalized proper nouns with lowercase function words; headings are
    almost entirely Title-Cased.
    """
    words = re.findall(r"[A-Za-z][A-Za-z\-/]*", unit)
    if len(words) < 3:
        return True
    remainder = words[1:]  # skip first word, which is always capitalized anyway
    cap_count = sum(1 for w in remainder if w[0].isupper())
    ratio = cap_count / len(remainder)
    return ratio > 0.6


def _clean_and_split(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    units = []
    for line in lines:
        line = re.sub(r'\s+', ' ', line)
        parts = re.split(r'(?<=[.!?])\s+', line)
        units.extend(p.strip() for p in parts if p.strip())

    filtered = []
    for u in units:
        words = u.split()
        if len(words) < 5:
            continue
        alpha_chars = sum(c.isalpha() or c.isspace() for c in u)
        if alpha_chars / max(len(u), 1) < 0.7:
            continue
        filtered.append(u)

    # Prefer genuine prose; only fall back to headings if nothing else exists.
    prose = [u for u in filtered if not _looks_like_heading(u)]
    return prose if prose else filtered


def analyze_resume_text(text):
    model, tokenizer = _load()
    sentences = _clean_and_split(text)

    if not sentences:
        return 0.0, []

    scored = []
    for s in sentences:
        ppl = _sentence_perplexity(s, model, tokenizer)
        if ppl is not None:
            ppl = min(ppl, 500)
            scored.append((s, ppl))

    if not scored:
        return 0.0, []

    perplexities = [p for _, p in scored]
    avg_ppl = sum(perplexities) / len(perplexities)

    mean = avg_ppl
    variance = sum((p - mean) ** 2 for p in perplexities) / len(perplexities)
    std_dev = variance ** 0.5
    burstiness = std_dev / mean if mean > 0 else 0

    perplexity_score = max(0, min(100, 100 - (avg_ppl - 30) * (100 / 180)))
    burstiness_score = max(0, min(100, 100 - burstiness * 150))
    overall_score = round((perplexity_score * 0.75 + burstiness_score * 0.25), 1)
    scored.sort(key=lambda x: x[1])
    flagged = [s for s, p in scored[:max(1, len(scored) // 4)]]

    return overall_score, flagged