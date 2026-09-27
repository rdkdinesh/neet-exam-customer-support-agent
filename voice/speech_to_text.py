import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def transcribe_audio(audio_file) -> str:

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=api_key
    )

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
        language="en",
        prompt=(
            "Indian NEET UG customer support. "
            "NEET, NTA, MBBS, BDS, medical admission, "
            "eligibility, counselling, syllabus, exam."
        )
    )

    return transcription.text.strip()