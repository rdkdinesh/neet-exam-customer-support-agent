from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import (
    MaxMessageTermination,
    TextMentionTermination
)

from agents.assistant_agent import create_assistant_agent
from agents.web_search_agent import create_web_search_agent
from agents.entry_agent import create_entry_agent


def create_team():

    # ---------------------------------------
    # Create agents
    # ---------------------------------------

    assistant_agent = create_assistant_agent()

    web_search_agent = create_web_search_agent()

    entry_agent = create_entry_agent()

    # ---------------------------------------
    # Termination conditions
    # ---------------------------------------

    max_message_termination = MaxMessageTermination(
        max_messages=6
    )

    text_mention_termination = TextMentionTermination(
        text="TERMINATE"
    )

    termination_condition = (
        max_message_termination |
        text_mention_termination
    )

    # ---------------------------------------
    # Round Robin Team
    # ---------------------------------------

    team = RoundRobinGroupChat(
        participants=[
            assistant_agent,
            web_search_agent,
            entry_agent
        ],
        termination_condition=termination_condition
    )

    return team