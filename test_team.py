import asyncio

from autogen_agentchat.ui import Console

from team.round_robin_team import create_team


async def main():

    team = create_team()

    task = """
    What is NEET UG and what are the eligibility requirements
    for appearing in the examination?
    """

    await Console(
        team.run_stream(
            task=task
        )
    )


if __name__ == "__main__":
    asyncio.run(main())