import os
from datetime import datetime


OUTPUT_DIR = "generated/conversations"


def write_conversation_to_file(
    query: str,
    answer_1: str,
    answer_2: str
) -> str:
    """
    Writes the user query and both agent answers to a text file.
    """

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        file_name = f"neet_conversation_{timestamp}.txt"

        file_path = os.path.join(
            OUTPUT_DIR,
            file_name
        )

        content = f"""
========================================
NEET MULTI-AGENT CUSTOMER SUPPORT
========================================

Timestamp:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

========================================
USER QUERY
========================================

{query}

========================================
ANSWER 1 - ASSISTANT AGENT
========================================

{answer_1}

========================================
ANSWER 2 - WEB SEARCH ASSISTANT
========================================

{answer_2}

========================================
END OF CONVERSATION
========================================
"""

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(content)

        return (
            f"Conversation successfully written to: "
            f"{file_path}"
        )

    except Exception as exc:

        return (
            f"Failed to write conversation file: "
            f"{str(exc)}"
        )