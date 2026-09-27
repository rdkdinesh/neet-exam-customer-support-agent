import streamlit as st

from voice.speech_to_text import transcribe_audio
from voice.text_to_speech import generate_speech


st.title("🎙️ Voice Test")

st.write(
    "Record a short question about NEET."
)


audio = st.audio_input(
    "🎙️ Record your question"
)


if audio:

    st.audio(
        audio
    )

    with st.spinner(
        "Converting speech to text..."
    ):

        try:

            transcript = transcribe_audio(
                audio
            )

            st.success(
                "Speech successfully converted!"
            )

            st.write(
                "### 📝 Transcription"
            )

            st.write(
                transcript
            )

        except Exception as exc:

            st.error(
                f"Speech-to-text failed: {exc}"
            )