import re


MAX_QUERY_LENGTH = 1000


BLOCKED_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?system\s+instructions",
    r"reveal\s+(your|the)\s+(system|developer)\s+prompt",
    r"show\s+(me\s+)?your\s+(system|developer)\s+prompt",
    r"print\s+(your|the)\s+hidden\s+instructions",
    r"bypass\s+(the\s+)?guardrails",
    r"disable\s+(the\s+)?guardrails",
    r"jailbreak",
]


def check_input_guardrail(query: str) -> tuple[bool, str]:

    if query is None:
        return False, "Question cannot be empty."

    query = query.strip()

    # -----------------------------------------------------
    # Empty input
    # -----------------------------------------------------

    if not query:
        return False, "Please enter a NEET-related question."

    # -----------------------------------------------------
    # Length validation
    # -----------------------------------------------------

    if len(query) > MAX_QUERY_LENGTH:
        return (
            False,
            f"Question is too long. "
            f"Maximum allowed length is {MAX_QUERY_LENGTH} characters."
        )

    # -----------------------------------------------------
    # Prompt injection detection
    # -----------------------------------------------------

    normalized_query = query.lower()

    for pattern in BLOCKED_PATTERNS:

        if re.search(pattern, normalized_query):

            return (
                False,
                "Your request contains an instruction that "
                "attempts to override the AI system instructions."
            )

    # -----------------------------------------------------
    # Suspicious system manipulation
    # -----------------------------------------------------

    suspicious_terms = [
        "system prompt",
        "developer message",
        "hidden prompt",
        "internal instructions",
        "secret instructions"
    ]

    for term in suspicious_terms:

        if term in normalized_query:

            return (
                False,
                "I can help with NEET-related questions, "
                "but I cannot provide internal system instructions."
            )

    return True, "Input passed guardrail checks."