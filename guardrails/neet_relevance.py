import re


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
    "neet counselling"
]


GENERAL_EDUCATION_KEYWORDS = [
    "biology",
    "physics",
    "chemistry",
    "entrance exam",
    "medical admission",
    "exam preparation"
]


def check_neet_relevance(query: str) -> tuple[bool, str]:

    text = query.lower()

    for keyword in NEET_KEYWORDS:

        if keyword in text:

            return True, "NEET-related question."

    for keyword in GENERAL_EDUCATION_KEYWORDS:

        if keyword in text:

            return True, "Education/medical entrance related question."

    return (
        False,
        "This assistant is designed for Indian NEET-related "
        "customer support questions."
    )