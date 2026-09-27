import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def generate_speech(text: str) -> bytes:

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    if not text:
        raise ValueError(
            "Text cannot be empty."
        )

    client = OpenAI(
        api_key=api_key
    )

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        response_format="mp3"
    )

    return response.read()