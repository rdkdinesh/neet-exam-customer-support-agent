import asyncio

from agents.web_search_agent import create_web_search_agent
from autogen_agentchat.ui import Console


async def main():

    agent = create_web_search_agent()

    question = """
    What is NEET UG and what are the eligibility requirements
    for appearing in the examination?
    """

    await Console(
        agent.run_stream(
            task=question
        )
    )


if __name__ == "__main__":
    asyncio.run(main())