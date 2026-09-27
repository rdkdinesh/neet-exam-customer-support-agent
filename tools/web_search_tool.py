import os

from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


# Stores the latest Tavily retrieval context.
# This is used by the DeepEval evaluation pipeline.
LAST_RETRIEVAL_CONTEXT = []


def get_last_retrieval_context():
    return LAST_RETRIEVAL_CONTEXT.copy()


def web_search(query: str) -> str:

    global LAST_RETRIEVAL_CONTEXT

    # Reset context for every new search
    LAST_RETRIEVAL_CONTEXT = []

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "TAVILY_API_KEY is not configured."

    try:

        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
            include_raw_content=False
        )

        results = response.get("results", [])

        if not results:
            return "No relevant web results were found."

        output = []

        # ---------------------------------------------------------
        # Tavily summary
        # ---------------------------------------------------------

        if response.get("answer"):

            output.append(
                f"WEB SEARCH SUMMARY:\n{response['answer']}"
            )

        output.append("\nWEB SOURCES:")

        # ---------------------------------------------------------
        # Capture retrieval context for DeepEval
        # ---------------------------------------------------------

        for index, result in enumerate(results, start=1):

            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            # Store retrieved information for evaluation
            LAST_RETRIEVAL_CONTEXT.append(
                f"""
Title: {title}
URL: {url}
Content:
{content}
""".strip()
            )

            output.append(
                f"""
SOURCE {index}
Title: {title}
URL: {url}
Content:
{content}
"""
            )

        return "\n".join(output)

    except Exception as exc:

        LAST_RETRIEVAL_CONTEXT = []

        return f"Web search failed: {str(exc)}"