"""
preprocessing.py — VaartaVerse Classical IR Pipeline
======================================================
Handles all text normalization before indexing and querying.

Pipeline:
    raw_text → lowercase → tokenize → stopword removal → WordNet Lemmatization → tokens

No external NLP LLM or embeddings — rule-based linguistic processing.
"""

import re
import string
from typing import Optional

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet

# Download required NLTK corpora on startup (idempotent)
for resource in ("stopwords", "wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)

_lemmatizer = WordNetLemmatizer()
_ENGLISH_STOPS = set(stopwords.words("english"))

# Domain stopwords specific to this folk tale corpus
_DOMAIN_STOPS = {
    "said", "one", "day", "went", "came", "upon", "time", "king", "great",
    "long", "also", "well", "good", "told", "man", "did", "two", "three",
    "come", "knew", "seen", "thus", "therefore", "replied",
}

ALL_STOPWORDS = _ENGLISH_STOPS | _DOMAIN_STOPS


def tokenize(text: str) -> list[str]:
    """
    Split text on whitespace and punctuation, lowercase all tokens.
    Replaces hyphens with spaces for compound words.
    """
    text = text.lower()
    text = text.replace("-", " ")
    tokens = re.findall(r"\b[a-z']+\b", text)
    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Filter tokens against English + domain stopword list and length > 1."""
    return [t for t in tokens if t not in ALL_STOPWORDS and len(t) > 1]


def lemmatize_tokens(tokens: list[str]) -> list[str]:
    """
    Apply WordNet Lemmatizer to each token.
    Lemmatizes first as noun then as verb for root dictionary forms.
    (e.g., 'tricked' -> 'trick', 'stories' -> 'story', 'feet' -> 'foot').
    """
    res = []
    for t in tokens:
        lemma = _lemmatizer.lemmatize(t, pos="n")
        lemma = _lemmatizer.lemmatize(lemma, pos="v")
        res.append(lemma)
    return res


# Alias for backward compatibility
stem_tokens = lemmatize_tokens


def preprocess(text: str, lemmatize: bool = True, stem: bool = True) -> list[str]:
    """
    Full preprocessing pipeline: tokenize → remove stopwords → lemmatize.

    Args:
        text:       Raw input text (query or document body).
        lemmatize:  If True (default), apply WordNet Lemmatization.
        stem:       Legacy flag alias for lemmatize.

    Returns:
        Ordered list of lemmatized tokens.
    """
    should_lemmatize = lemmatize and stem
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    if should_lemmatize:
        tokens = lemmatize_tokens(tokens)
    return tokens


def preprocess_zones(title: str, body: str, lemmatize: bool = True, stem: bool = True) -> dict:
    """
    Preprocess a document split into named zones (title, body).
    Returns a dict with per-zone tokens and a combined token list.
    """
    title_tokens = preprocess(title, lemmatize=lemmatize, stem=stem)
    body_tokens = preprocess(body, lemmatize=lemmatize, stem=stem)
    return {
        "title": title_tokens,
        "body": body_tokens,
        "all": title_tokens + body_tokens,
    }
