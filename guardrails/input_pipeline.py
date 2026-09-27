from guardrails.input_guardrail import check_input_guardrail
from guardrails.neet_relevance import check_neet_relevance


def validate_user_input(query: str) -> tuple[bool, str]:

    # -----------------------------------------------------
    # Security checks
    # -----------------------------------------------------

    allowed, message = check_input_guardrail(query)

    if not allowed:
        return False, message

    # -----------------------------------------------------
    # Domain relevance checks
    # -----------------------------------------------------

    allowed, message = check_neet_relevance(query)

    if not allowed:
        return False, message

    return True, "Input approved."