import asyncio

from team.round_robin_team import create_team
from tools.web_search_tool import get_last_retrieval_context


def extract_content(raw_content):

    if isinstance(raw_content, str):
        return raw_content

    if isinstance(raw_content, list):

        parts = []

        for item in raw_content:

            if isinstance(item, str):

                parts.append(item)

            elif isinstance(item, dict):

                if item.get("text"):
                    parts.append(
                        str(item["text"])
                    )

                elif item.get("content"):
                    parts.append(
                        str(item["content"])
                    )

            else:

                text_value = getattr(
                    item,
                    "text",
                    None
                )

                if text_value:
                    parts.append(
                        str(text_value)
                    )

        return "\n".join(parts)

    return str(raw_content)


async def execute_autogen(question):

    team = create_team()

    try:

        result = await team.run(task=question)

        retrieval_context = get_last_retrieval_context()

        final_answer = ""
        assistant_answer = ""
        web_search_answer = ""

        messages = []

        for message in result.messages:

            source = getattr(message, "source", "")
            raw_content = getattr(message, "content", "")

            content = extract_content(raw_content).strip()

            if not content:
                continue

            if content.upper() == "TERMINATE":
                continue

            messages.append(
                {
                    "source": source,
                    "content": content
                }
            )

            # ---------------------------------------------
            # Assistant Agent answer
            # ---------------------------------------------

            if source == "assistant_agent":

                assistant_answer = content

            # ---------------------------------------------
            # Web Search Agent answer
            # ---------------------------------------------

            elif source == "web_search_assistant":

                web_search_answer = content

            # ---------------------------------------------
            # Entry Agent answer
            # ---------------------------------------------

            elif source == "entry_agent":

                final_answer = content

        # -------------------------------------------------
        # Evaluation answer selection
        # -------------------------------------------------
        #
        # For current NEET questions, prefer the answer
        # produced by the Web Search Agent because it
        # contains current web-grounded information.
        #
        # If Web Search Agent did not produce an answer,
        # fall back to Assistant Agent.
        #
        # Entry Agent may contain only the file-write
        # confirmation, so don't blindly use it.
        # -------------------------------------------------

        evaluation_answer = ""

        if web_search_answer:
            evaluation_answer = web_search_answer

        elif assistant_answer:
            evaluation_answer = assistant_answer

        elif final_answer:
            evaluation_answer = final_answer



        print()
        print("=" * 70)
        print("EVALUATION ANSWER SELECTION")
        print("=" * 70)

        print("Assistant Agent answer length:",
            len(assistant_answer))

        print("Web Search Agent answer length:",
            len(web_search_answer))

        print("Entry Agent answer length:",
            len(final_answer))

        print("Selected evaluation answer length:",
            len(evaluation_answer))

        print("=" * 70)

        return {
            "answer": evaluation_answer,
            "assistant_answer": assistant_answer,
            "web_search_answer": web_search_answer,
            "entry_answer": final_answer,
            "messages": messages,
            "retrieval_context": retrieval_context
        }

    finally:

        await asyncio.sleep(0)


async def execute_all_questions(questions):

    results = []

    for question in questions:

        print()
        print("=" * 70)
        print("QUESTION")
        print("=" * 70)

        print(question)

        result = await execute_autogen(
            question
        )

        results.append(
            result
        )

    return results