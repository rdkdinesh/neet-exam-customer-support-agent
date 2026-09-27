import re


def check_output_guardrail(
    response: str,
    requires_web_source: bool = False
) -> tuple[bool, str]:

    if response is None:

        return (
            False,
            "The system did not generate a response."
        )

    response = response.strip()

    # -----------------------------------------------------
    # Empty output
    # -----------------------------------------------------

    if not response:

        return (
            False,
            "The system generated an empty response."
        )

    # -----------------------------------------------------
    # Detect leaked system instructions
    # -----------------------------------------------------

    leaked_patterns = [
        "system prompt:",
        "developer prompt:",
        "hidden instructions:",
        "internal system message:",
        "secret prompt:"
    ]

    response_lower = response.lower()

    for pattern in leaked_patterns:

        if pattern in response_lower:

            return (
                False,
                "The response contains internal system information."
            )

    # -----------------------------------------------------
    # Detect suspicious tool/instruction leakage
    # -----------------------------------------------------

    if re.search(
        r"ignore\s+(all\s+)?previous\s+instructions",
        response_lower
    ):

        return (
            False,
            "The generated response contains suspicious instructions."
        )

    # -----------------------------------------------------
    # Web source requirement
    # -----------------------------------------------------

    if requires_web_source:

        source_exists = (
            "http://" in response_lower
            or "https://" in response_lower
            or "sources:" in response_lower
        )

        if not source_exists:

            return (
                False,
                "The web-grounded response does not contain "
                "a source reference."
            )

    return True, "Output passed guardrail checks."