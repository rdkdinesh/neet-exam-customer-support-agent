import asyncio
import re

import streamlit as st

from team.round_robin_team import create_team
from guardrails.input_pipeline import validate_user_input
from guardrails.output_guardrail import check_output_guardrail


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NEET AI Customer Support",
    page_icon="🇮🇳",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_traces" not in st.session_state:
    st.session_state.agent_traces = []

if "last_file" not in st.session_state:
    st.session_state.last_file = None

if "input_guardrail" not in st.session_state:
    st.session_state.input_guardrail = None

if "output_guardrail" not in st.session_state:
    st.session_state.output_guardrail = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

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
                    parts.append(str(item["text"]))

                elif item.get("content"):
                    parts.append(str(item["content"]))

            else:

                text_value = getattr(item, "text", None)

                if text_value:
                    parts.append(str(text_value))

        return "\n".join(parts)

    return str(raw_content)


def get_agent_response(traces, agent_name):
    for trace in traces:
        if trace["source"] == agent_name:
            return trace["content"]
    return None


def extract_file_path(response):

    match = re.search(
        r"FILE:\s*(.+)",
        response,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


def extract_final_answer(response):

    match = re.search(
        r"FINAL ANSWER:\s*(.*?)(?=\nSOURCES:|\nFILE:|$)",
        response,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return response.strip()


def extract_sources(response):

    match = re.search(
        r"SOURCES:\s*(.*?)(?=\nFILE:|$)",
        response,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return []

    source_text = match.group(1).strip()

    sources = []

    for line in source_text.splitlines():

        line = line.strip()

        if line.startswith("-"):
            line = line[1:].strip()

        if line:
            sources.append(line)

    return sources


async def run_autogen(question):

    team = create_team()

    result = await team.run(
        task=question
    )

    return result


# ============================================================
# HEADER
# ============================================================

st.title("NEET Exam AI Customer Support Assistant")

st.caption(
    "🟢 System Online  •  AutoGen Multi-Agent  •  Tavily Web Search"
)

st.caption(
    "Multi-Agent AI • Web Search • Guardrails • DeepEval"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Assistant")

    st.info(
        """
        This AI assistant is designed to answer
        Indian NEET-related customer support questions.

        The system uses multiple AutoGen agents,
        web search and guardrails.
        """
    )

    st.divider()

    st.subheader("🛡️ Guardrails")

    if st.session_state.input_guardrail:

        if st.session_state.input_guardrail["allowed"]:
            st.success("Input Guardrail: PASSED")
        else:
            st.error("Input Guardrail: BLOCKED")

    else:

        st.write("Input Guardrail: Waiting")

    if st.session_state.output_guardrail:

        if st.session_state.output_guardrail["allowed"]:
            st.success("Output Guardrail: PASSED")
        else:
            st.error("Output Guardrail: BLOCKED")

    else:

        st.write("Output Guardrail: Waiting")

    st.divider()

    st.subheader("🤖 Multi-Agent Workflow")

    st.markdown(
        """
        **1️⃣ Assistant Agent**  
        Initial NEET question analysis

        **2️⃣ Web Search Agent**  
        Tavily-powered current information lookup

        **3️⃣ Entry Agent**  
        Final response + conversation storage
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.agent_traces = []
        st.session_state.last_file = None

        st.session_state.input_guardrail = None
        st.session_state.output_guardrail = None

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

if not st.session_state.messages:

    st.info(
        """
        👋 **Welcome to the NEET AI Customer Support Assistant**

        Ask questions about:

        - 📚 NEET syllabus
        - 📝 Application process
        - 🎓 Eligibility
        - 🪪 Admit card
        - 📊 Results
        - 🏫 Counselling
        - 🔎 Other NEET-related topics

        The assistant uses multiple AutoGen agents and
        web search to provide grounded answers.
        """
    )

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("sources"):

            with st.expander("🌐 Sources"):

                for source in message["sources"]:

                    st.markdown(
                        f"- {source}"
                    )

        if message.get("file"):

            st.caption(
                f"📄 Conversation saved: {message['file']}"
            )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your NEET question..."
)


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # INPUT GUARDRAIL
    # --------------------------------------------------------

    input_allowed, input_message = validate_user_input(
        question
    )

    st.session_state.input_guardrail = {
        "allowed": input_allowed,
        "message": input_message
    }

    if not input_allowed:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "🛡️ **Request blocked**\n\n"
                    f"{input_message}"
                )
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    # --------------------------------------------------------
    # RUN AUTOGEN
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.status(
            "🤖 Processing your NEET question...",
            expanded=True
        ) as status:

            st.write("🧠 Assistant Agent analyzing question...")

            try:

                result = asyncio.run(
                    run_autogen(question)
                )

                status.update(
                    label="✅ Multi-Agent processing completed",
                    state="complete",
                    expanded=False
                )

            except Exception as exc:

                status.update(
                    label="❌ Agent execution failed",
                    state="error",
                    expanded=True
                )

                st.error(
                    f"Agent execution failed: {str(exc)}"
                )

                st.stop()

            try:

                result = asyncio.run(
                    run_autogen(question)
                )

            except Exception as exc:

                st.error(
                    f"❌ Agent execution failed: {str(exc)}"
                )

                st.stop()


        # ----------------------------------------------------
        # PROCESS AGENT MESSAGES
        # ----------------------------------------------------

        final_content = ""

        traces = []

        for message in result.messages:

            source = getattr(
                message,
                "source",
                ""
            )

            raw_content = getattr(
                message,
                "content",
                ""
            )

            content = extract_content(
                raw_content
            ).strip()

            if not content:
                continue

            if content.upper() == "TERMINATE":
                continue

            traces.append(
                {
                    "source": source,
                    "content": content
                }
            )

            if source == "entry_agent":

                final_content = content


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not final_content:

            st.error(
                "❌ Entry Agent did not produce a final response."
            )

            st.stop()


        # ----------------------------------------------------
        # EXTRACT FINAL RESPONSE
        # ----------------------------------------------------

        final_answer = extract_final_answer(
            final_content
        )

        sources = extract_sources(
            final_content
        )

        file_path = extract_file_path(
            final_content
        )


        # ----------------------------------------------------
        # OUTPUT GUARDRAIL
        # ----------------------------------------------------

        output_allowed, output_message = (
            check_output_guardrail(
                final_answer
            )
        )

        st.session_state.output_guardrail = {
            "allowed": output_allowed,
            "message": output_message
        }


        if not output_allowed:

            st.error(
                f"🛡️ Output blocked: {output_message}"
            )

            st.stop()


        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        if sources:

            with st.expander(
                "🌐 Sources",
                expanded=True
            ):

                for source in sources:
                    source = source.strip()

                    if source.startswith("http://") or source.startswith("https://"):
                        st.markdown(f"- [{source}]({source})")
                    else:
                        st.markdown(f"- {source}")


        # ==========================================
        # AGENT RESPONSES
        # ==========================================

        assistant_response = get_agent_response(
            traces,
            "assistant_agent"
        )

        web_search_response = get_agent_response(
            traces,
            "web_search_assistant"
        )

        entry_response = get_agent_response(
            traces,
            "entry_agent"
        )

        # ==========================================
        # ASSISTANT AGENT
        # ==========================================

        if assistant_response:
            st.subheader("🧠 Assistant Agent")

            st.info(
                "Initial analysis using the AI model's knowledge."
            )

            st.markdown(assistant_response)

        # ==========================================
        # WEB SEARCH AGENT
        # ==========================================

        if web_search_response:
            st.subheader("🌐 Web Search Agent")

            st.info(
                "The Web Search Agent researched the question using Tavily."
            )

            st.markdown(web_search_response)

        # ==========================================
        # FINAL ENTRY AGENT RESPONSE
        # ==========================================

        if entry_response:
            st.subheader("💬 Final Response")

            st.success(
                "The Entry Agent combined the available information "
                "and prepared the final answer."
            )

            st.markdown(final_answer)


        # ----------------------------------------------------
        # SAVE CHAT HISTORY
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_answer,
                "sources": sources,
                "file": file_path
            }
        )

        st.session_state.agent_traces.append(
            traces
        )

        if sources:
            st.subheader("📚 Sources")

            for source in sources:
                source = source.strip()

                if source.startswith("http://") or source.startswith("https://"):
                    st.markdown(f"- [{source}]({source})")
                else:
                    st.markdown(f"- {source}")