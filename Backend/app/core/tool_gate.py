import re

DOC_TRIGGER_PATTERN = re.compile(
    r"""
    \bpage\s*\d+\b |
    \bpages?\b |
    \bsection\s*\d*\b |
    \bchapter\s*\d*\b |
    \btable\s+of\s+contents\b |
    \bhow\s+many\s+(pages|sections|chapters)\b |
    \b(summarize|explain|describe)\b.*\b(page|section|chapter|doc|document|pdf|file)\b |
    \b(quote|exact\s+wording|verbatim)\b |
    \bdoc(ument)?\b |
    \bpdf\b |
    \battach(ed|ment)?\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

def requires_forced_retrieval(user_message: str) -> bool:
    return bool(DOC_TRIGGER_PATTERN.search(user_message))