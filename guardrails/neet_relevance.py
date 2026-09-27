NEET_KEYWORDS = [
    "neet",
    "neet ug",
    "neet-ug",
    "nta",
    "medical entrance",
    "mbbs",
    "bds",
    "medical college",
    "neet application",
    "neet exam",
    "neet eligibility",
    "neet syllabus",
    "neet result",
    "neet counselling",
    "neet admit card",
    "neet registration",
    "neet cutoff",
    "neet score",
    "neet rank",
    "neet preparation",
    "neet question",
    "neet counselling",
    "exam",
    "admit card",
    "application",
    "registration",
    "result",
    "counselling",
    "eligibility",
    "syllabus",
    "entrance",
    "medical"
]

GENERAL_EDUCATION_KEYWORDS = [
    "biology",
    "physics",
    "chemistry",
    "education",
    "study",
    "student",
    "college",
    "university",
    "course",
    "career"
]


def check_neet_relevance(query: str) -> tuple[bool, str]:

    text = query.lower().strip()

    # Explicit NEET / education related question
    for keyword in NEET_KEYWORDS:
        if keyword in text:
            return True, "NEET-related question."

    # General education question
    for keyword in GENERAL_EDUCATION_KEYWORDS:
        if keyword in text:
            return True, "Education-related question."

    # Allow short conversational questions.
    # The agents can determine the actual intent.
    if len(text.split()) <= 5:
        return True, "Short conversational question."

    # Keep clearly unrelated long questions blocked.
    return False, (
        "This assistant is designed for Indian NEET-related "
        "customer support questions."
    )