"""Education institution filtering utilities for resume parsing.

Provides keyword sets, regex patterns, and classification functions to
distinguish educational institutions from employers and skill/tool names
that spaCy may incorrectly tag as ORG entities.
"""

import re
from typing import Set


# Keywords that indicate an educational institution (lowercase)
EDUCATION_KEYWORDS: Set[str] = {
    'university', 'college', 'school', 'institute', 'academy',
    'gpa', 'bachelor', 'master', 'phd', 'degree', 'coursework',
    'expected', 'graduated', 'graduation', 'portfolio', 'education',
    'bootcamp', 'secondary', 'polytechnic',
}

# Compiled regex patterns that match education-related entity names
EDUCATION_PATTERNS = [
    re.compile(r'university\s+of\s+\w+', re.IGNORECASE),
    re.compile(r'\w+\s+university', re.IGNORECASE),
    re.compile(r'\w+\s+college', re.IGNORECASE),
    re.compile(r'college\s+of\s+\w+', re.IGNORECASE),
    re.compile(r'\w+\s+institute\s+of\s+\w+', re.IGNORECASE),
    re.compile(r'\w+\s+academy', re.IGNORECASE),
    re.compile(r'\w+\s+school', re.IGNORECASE),
    re.compile(r'\w+\s+polytechnic', re.IGNORECASE),
    re.compile(r'bachelor\s+of\s+\w+', re.IGNORECASE),
    re.compile(r'master\s+of\s+\w+', re.IGNORECASE),
    re.compile(r'expected\s+.*\d{4}', re.IGNORECASE),
]

# Skills / tools that spaCy frequently misclassifies as ORG (lowercase)
SKILL_KEYWORDS: Set[str] = {
    'github', 'gitlab', 'docker', 'kubernetes', 'jenkins', 'aws',
    'azure', 'gcp', 'android', 'ios', 'linux', 'windows', 'macos',
    'python', 'java', 'javascript', 'typescript', 'react', 'angular',
    'django', 'flask', 'fastapi', 'mongodb', 'postgresql', 'mysql',
    'redis', 'elasticsearch', 'dynamodb', 'node.js', 'express',
    'spring', 'android development', 'compilers', 'data science',
}

# Context words that suggest an education section
_EDUCATION_CONTEXT_WORDS: Set[str] = {
    'bachelor', 'master', 'phd', 'gpa', 'graduated', 'graduation',
    'degree', 'coursework', 'thesis', 'dean', 'honors', 'summa',
    'magna', 'cum laude', 'diploma', 'academic',
}

# Context words that suggest an employment section
_EMPLOYMENT_CONTEXT_WORDS: Set[str] = {
    'intern', 'engineer', 'developer', 'manager', 'director', 'lead',
    'architect', 'analyst', 'consultant', 'coordinator', 'specialist',
    'designed', 'built', 'implemented', 'developed', 'led', 'managed',
    'collaborated', 'deployed', 'responsible',
}


def is_educational_institution(text: str) -> bool:
    """Check whether *text* refers to an educational institution.

    Uses both keyword containment (any word from ``EDUCATION_KEYWORDS``
    appears inside *text*) and regex pattern matching against
    ``EDUCATION_PATTERNS``.

    Returns ``True`` if the text looks like an educational institution,
    ``False`` otherwise.
    """
    if not text or len(text.strip()) < 2:
        return False

    text_lower = text.lower()

    # Keyword check
    if any(kw in text_lower for kw in EDUCATION_KEYWORDS):
        return True

    # Pattern check
    for pattern in EDUCATION_PATTERNS:
        if pattern.search(text_lower):
            return True

    return False


def classify_organization(org_name: str, context: str = "") -> str:
    """Classify an organisation name as ``'education'`` or ``'employment'``.

    1. If the org name itself looks educational (via ``is_educational_institution``),
       return ``'education'`` immediately.
    2. Otherwise, fall back to context-aware keyword analysis — count
       education-context vs employment-context words in the surrounding text.
    3. If neither signal dominates, default to ``'employment'``.
    """
    if is_educational_institution(org_name):
        return 'education'

    if not context:
        return 'employment'

    context_lower = context.lower()

    edu_score = sum(1 for w in _EDUCATION_CONTEXT_WORDS if w in context_lower)
    emp_score = sum(1 for w in _EMPLOYMENT_CONTEXT_WORDS if w in context_lower)

    if edu_score > emp_score:
        return 'education'

    return 'employment'
