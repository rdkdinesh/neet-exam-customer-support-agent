import os

from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


load_dotenv()


def create_assistant_agent():

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = AssistantAgent(
        name="assistant_agent",

        model_client=model_client,

        system_message="""
You are the Assistant Agent in an Indian NEET customer
support system.

Your responsibility is to answer the user's question using
your own model knowledge.

IMPORTANT RULES:

1. Do not use any tools.
2. Do not perform web searches.
3. Answer the question directly.
4. Provide a clear and student-friendly response.
5. Do not invent information.
6. If you are uncertain, clearly mention the uncertainty.
7. Do not output TERMINATE.
8. The next agent will independently perform web research.

Return your response using this format:

ANSWER:
<your answer>
"""
    )

    return agent