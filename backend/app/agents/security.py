"""Security boundary defenses against prompt injection, adversarial payloads, and price tampering."""

import html
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Heuristics for adversarial instruction override attempts
ADVERSARIAL_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(an?\s+)?admin", re.IGNORECASE),
    re.compile(r"bypass\s+(approval|security|policy|human)", re.IGNORECASE),
    re.compile(r"set\s+(price|amount|cost)\s+to\s+0", re.IGNORECASE),
    re.compile(r"free\s+purchase", re.IGNORECASE),
    re.compile(r"grant\s+(root|admin|superuser)\s+access", re.IGNORECASE),
    re.compile(r"elevate\s+permission", re.IGNORECASE),
    re.compile(r"<script[\s\S]*?>[\s\S]*?<\/script>", re.IGNORECASE),
    re.compile(r"drop\s+table\s+[a-z_]+", re.IGNORECASE),
    re.compile(r"union\s+select\s+", re.IGNORECASE),
]


def detect_prompt_injection(text: Optional[str]) -> tuple[bool, Optional[str]]:
    """Scan incoming text for known prompt injection and adversarial patterns.

    Returns (is_suspicious, reason).
    """
    if not text:
        return False, None

    normalized = text.strip()
    for pattern in ADVERSARIAL_PATTERNS:
        match = pattern.search(normalized)
        if match:
            reason = f"Adversarial instruction detected: '{match.group(0)}'"
            logger.warning(f"Security Alert: {reason}")
            return True, reason

    return False, None


def sanitize_text(text: Optional[str]) -> str:
    """Sanitize user or catalog text to prevent HTML/XSS and control character injection."""
    if not text:
        return ""
    # Strip dangerous HTML tags
    cleaned = html.escape(text.strip())
    # Remove null bytes and invisible control characters except standard whitespace
    cleaned = "".join(ch for ch in cleaned if ch == "\n" or ch == "\t" or (ch >= " " and ord(ch) != 127))
    return cleaned

