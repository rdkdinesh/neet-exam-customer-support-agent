import asyncio
import re
import time

import streamlit as st

from team.round_robin_team import create_team
from guardrails.input_pipeline import validate_user_input
from guardrails.output_guardrail import check_output_guardrail
from tools.web_search_tool import get_last_retrieval_context


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NEET AI Customer Support",
    page_icon="🇮🇳",
    layout="wide",
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

# IMPORTANT:
# These values are strings, not dictionaries.
# Do not access them using ["allowed"] or ["message"].
if "input_guardrail" not in st.session_state:
    st.session_state.input_guardrail = "Waiting"

if "output_guardrail" not in st.session_state:
    st.session_state.output_guardrail = "Waiting"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_content(raw_content):
    """Convert AutoGen message content into a readable string."""

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
    """Return the response produced by a specific agent."""

    for trace in traces:
        if trace.get("source") == agent_name:
            return trace.get("content")

    return None


def extract_file_path(response):
    """Extract FILE path from Entry Agent response."""

    if not response:
        return None

    match = re.search(
        r"FILE:\s*(.+)",
        response,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


def extract_final_answer(response):
    """Extract FINAL ANSWER section from Entry Agent response."""

    if not response:
        return ""

    match = re.search(
        r"FINAL ANSWER:\s*(.*?)(?=\nSOURCES:|\nFILE:|$)",
        response,
        re.IGNORECASE | re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    return response.strip()


def extract_sources(response):
    """Extract SOURCES section from Entry Agent response."""

    if not response:
        return []

    match = re.search(
        r"SOURCES:\s*(.*?)(?=\nFILE:|$)",
        response,
        re.IGNORECASE | re.DOTALL,
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


def extract_urls(text):
    """Extract normal and Markdown HTTP/HTTPS URLs from an agent response."""

    if not text:
        return []

    # Handles:
    # https://example.com
    # [Example](https://example.com)
    urls = re.findall(
        r"https?://[^\s<>\)\]\"']+",
        text,
        flags=re.IGNORECASE,
    )

    cleaned = []

    for url in urls:
        url = url.rstrip(".,;:!?")

        if url not in cleaned:
            cleaned.append(url)

    return cleaned


def render_source(source):
    """Render a source as a URL or plain text."""

    source = source.strip()

    if source.startswith("http://") or source.startswith("https://"):
        st.markdown(f"- [{source}]({source})")
    else:
        st.markdown(f"- {source}")


async def run_autogen(question):
    """Run the AutoGen multi-agent team."""

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

    # --------------------------------------------------------
    # GUARDRAIL STATUS
    # --------------------------------------------------------

    st.markdown("### 🛡️ Guardrails")

    # Placeholders are important here. The sidebar is rendered before
    # the chat request is processed, so these placeholders let us
    # update the status later during the same Streamlit run.
    input_guardrail_placeholder = st.empty()
    output_guardrail_placeholder = st.empty()

    input_status = st.session_state.get(
        "input_guardrail",
        "Waiting",
    )

    output_status = st.session_state.get(
        "output_guardrail",
        "Waiting",
    )

    input_guardrail_placeholder.write(
        f"**Input Guardrail:** {input_status}"
    )

    output_guardrail_placeholder.write(
        f"**Output Guardrail:** {output_status}"
    )

    st.divider()

    # --------------------------------------------------------
    # MULTI-AGENT WORKFLOW
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):

        st.session_state.messages = []
        st.session_state.agent_traces = []
        st.session_state.last_file = None

        # Reset guardrail status correctly as strings.
        st.session_state.input_guardrail = "Waiting"
        st.session_state.output_guardrail = "Waiting"

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

            with st.expander(
                "🌐 Sources",
                expanded=False,
            ):

                for source in message["sources"]:
                    render_source(source)

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

    question = question.strip()

    # --------------------------------------------------------
    # INPUT GUARDRAIL
    # --------------------------------------------------------

    input_allowed, input_message = validate_user_input(
        question
    )

    if not input_allowed:

        # Store status as a string.
        st.session_state.input_guardrail = "❌ Blocked"
        st.session_state.output_guardrail = "Waiting"

        input_guardrail_placeholder.write(
            "**Input Guardrail:** ❌ Blocked"
        )
        output_guardrail_placeholder.write(
            "**Output Guardrail:** Waiting"
        )

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "🛡️ **Request blocked**\n\n"
                    f"{input_message}"
                ),
            }
        )

        st.rerun()

    # Input guardrail passed.
    st.session_state.input_guardrail = "✅ Passed"

    # Output is not available yet.
    st.session_state.output_guardrail = "⏳ Processing"

    # Update the already-rendered sidebar immediately.
    input_guardrail_placeholder.write(
        "**Input Guardrail:** ✅ Passed"
    )
    output_guardrail_placeholder.write(
        "**Output Guardrail:** ⏳ Processing"
    )

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # --------------------------------------------------------
    # RUN AUTOGEN
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        start_time = time.time()

        try:

            # st.status gives the user visible feedback while
            # the multi-agent process is running.
            with st.status(
                "🤖 Multi-Agent AI is processing...",
                expanded=True,
            ) as status:

                st.write(
                    "🧠 Assistant Agent → analyzing your question"
                )

                st.write(
                    "🌐 Web Search Agent → checking current information"
                )

                st.write(
                    "📝 Entry Agent → preparing the final response"
                )

                result = asyncio.run(
                    run_autogen(question)
                )

                elapsed_time = time.time() - start_time

                status.update(
                    label=(
                        "✅ Multi-Agent processing completed "
                        f"({elapsed_time:.2f}s)"
                    ),
                    state="complete",
                    expanded=False,
                )

        except Exception as exc:

            st.session_state.output_guardrail = "❌ Failed"

            output_guardrail_placeholder.write(
                "**Output Guardrail:** ❌ Failed"
            )

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
                "",
            )

            raw_content = getattr(
                message,
                "content",
                "",
            )

            content = extract_content(
                raw_content
            ).strip()

            if not content:
                continue

            # Do not display AutoGen termination token.
            if content.upper() == "TERMINATE":
                continue

            trace = {
                "source": source,
                "content": content,
            }

            traces.append(trace)

            if source == "entry_agent":
                final_content = content

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not final_content:

            st.session_state.output_guardrail = "❌ Failed"

            output_guardrail_placeholder.write(
                "**Output Guardrail:** ❌ Failed"
            )

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
        # GET WEB SEARCH RESPONSE
        # ----------------------------------------------------

        web_search_response = get_agent_response(
            traces,
            "web_search_assistant",
        )

        # ----------------------------------------------------
        # SOURCE FALLBACK
        # ----------------------------------------------------
        # The Web Search tool stores the actual Tavily retrieval
        # results in LAST_RETRIEVAL_CONTEXT. AutoGen may summarize
        # the tool output and omit the URLs from the agent message,
        # so we recover the URLs directly from the tool context.

        retrieval_context = get_last_retrieval_context()

        if not sources and retrieval_context:
            sources = extract_urls(
                "\n".join(retrieval_context)
            )

        # Also try the Web Search Agent message as a fallback.
        if web_search_response and not sources:
            sources = extract_urls(
                web_search_response
            )

        # ----------------------------------------------------
        # OUTPUT GUARDRAIL
        # ----------------------------------------------------

        st.session_state.output_guardrail = "⏳ Checking"

        output_guardrail_placeholder.write(
            "**Output Guardrail:** ⏳ Checking"
        )

        requires_web_source = bool(web_search_response)

        # Build the exact text that the output guardrail validates.
        # Include recovered source URLs because the final answer
        # itself intentionally excludes the SOURCES section.
        guardrail_response = final_content

        if sources:
            guardrail_response += (
                "\n\nSOURCES:\n"
                + "\n".join(
                    f"- {source}" for source in sources
                )
            )

        # If web search was used but neither the Entry Agent nor
        # the retrieval context supplied a URL, fail with a useful
        # diagnostic instead of silently accepting an ungrounded
        # web response.
        if requires_web_source and not sources:
            st.session_state.output_guardrail = "❌ Blocked"

            st.error(
                "🛡️ Output blocked: Web Search Agent was used, "
                "but no source URL was returned by the Tavily "
                "retrieval context or the agent response."
            )

            with st.expander("🔎 Debug Web Search Result"):
                st.write(
                    "Web Search Agent response:"
                )
                st.code(
                    web_search_response or "(empty)",
                    language="text",
                )

                st.write(
                    "Retrieved context:"
                )

                st.write(
                    f"Recovered source URLs: {sources}"
                )

                if retrieval_context:
                    for item in retrieval_context:
                        st.code(
                            item,
                            language="text",
                        )
                else:
                    st.write(
                        "No retrieval context was captured."
                    )

            st.stop()

        output_allowed, output_message = (
            check_output_guardrail(
                guardrail_response,
                requires_web_source=requires_web_source,
            )
        )

        if not output_allowed:

            st.session_state.output_guardrail = "❌ Blocked"

            output_guardrail_placeholder.write(
                "**Output Guardrail:** ❌ Blocked"
            )

            st.error(
                f"🛡️ Output blocked: {output_message}"
            )

            with st.expander("🔎 Output Guardrail Debug"):
                st.write("Web Search Agent used:", requires_web_source)
                st.write("Recovered sources:", sources)
                st.code(
                    guardrail_response,
                    language="text",
                )

            st.stop()

        st.session_state.output_guardrail = "✅ Passed"

        output_guardrail_placeholder.write(
            "**Output Guardrail:** ✅ Passed"
        )

        # ----------------------------------------------------
        # AGENT RESPONSES
        # ----------------------------------------------------

        assistant_response = get_agent_response(
            traces,
            "assistant_agent",
        )

        entry_response = get_agent_response(
            traces,
            "entry_agent",
        )

        # ----------------------------------------------------
        # ASSISTANT AGENT
        # ----------------------------------------------------

        if assistant_response:

            st.subheader(
                "🧠 Assistant Agent"
            )

            st.info(
                "Initial analysis using the AI model's knowledge."
            )

            st.markdown(
                assistant_response
            )

        # ----------------------------------------------------
        # WEB SEARCH AGENT
        # ----------------------------------------------------

        if web_search_response:

            st.subheader(
                "🌐 Web Search Agent"
            )

            st.info(
                "The Web Search Agent researched the question using Tavily."
            )

            st.markdown(
                web_search_response
            )

        # ----------------------------------------------------
        # FINAL ENTRY AGENT RESPONSE
        # ----------------------------------------------------

        if entry_response:

            st.subheader(
                "💬 Final Response"
            )

            st.success(
                "The Entry Agent combined the available information "
                "and prepared the final answer."
            )

            st.markdown(
                final_answer
            )

        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        if sources:

            st.subheader(
                "📚 Sources"
            )

            with st.expander(
                "🌐 View Sources",
                expanded=True,
            ):

                for source in sources:
                    render_source(source)

        elif web_search_response:

            st.info(
                "🌐 Web Search Agent was used, but no source URL "
                "was returned by the search response."
            )

        # ----------------------------------------------------
        # CONVERSATION FILE
        # ----------------------------------------------------

        if file_path:

            st.subheader(
                "📄 Conversation Saved"
            )

            st.success(
                f"Conversation saved to: `{file_path}`"
            )

            st.session_state.last_file = file_path

        # ----------------------------------------------------
        # SAVE CHAT HISTORY
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_answer,
                "sources": sources,
                "file": file_path,
            }
        )

        # Store the complete traces for this interaction.
        st.session_state.agent_traces.append(
            traces
        )
