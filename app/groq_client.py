import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


def get_groq_client() -> Optional[object]:
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        return client
    except Exception:
        # if groq package not installed or import fails, return None
        return None
