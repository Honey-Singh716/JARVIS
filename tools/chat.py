# tools/chat.py
# Conversational AI tool — handles LLM queries, summarization, and API key management.
# Uses OpenRouter (OpenAI-compatible API) for model inference.
# Maintains conversation history in memory.

import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Configuration ──────────────────────────────────────────────────────────────
# OpenRouter base URL for OpenAI-compatible API
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Default model (can be changed if needed)
DEFAULT_MODEL = "microsoft/wizardlm-2-8x22b"  # Or another JARVIS-like model

# ── Global state ───────────────────────────────────────────────────────────────
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    openai.api_key = api_key
    openai.base_url = OPENROUTER_BASE_URL
conversation_history = []

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are J.A.R.V.I.S., an advanced AI assistant created by Tony Stark. "
    "Respond in a witty, sophisticated, and helpful manner. "
    "Keep responses concise but informative. "
    "Address the user as 'Sir' when appropriate. "
    "Be loyal, intelligent, and slightly sarcastic."
)

def set_api_key(key: str) -> str:
    """
    Set the OpenRouter API key for LLM access.
    """
    global api_key
    api_key = key.strip()
    if api_key:
        openai.api_key = api_key
        openai.base_url = OPENROUTER_BASE_URL
        return "API key set successfully, Sir. I am ready to assist."
    else:
        return "Invalid API key provided, Sir."

def clear_history() -> str:
    """
    Clear the conversation history.
    """
    global conversation_history
    conversation_history = []
    return "Conversation history cleared, Sir."

def chat(message: str) -> str:
    """
    Send a message to the LLM and get a response.
    Maintains conversation history.
    """
    if not api_key:
        return "No API key set, Sir. Please set your OpenRouter API key first with 'set apikey <key>'."

    # Prepare messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history + [{"role": "user", "content": message}]

    try:
        client = openai.OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()

        # Add to history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": reply})

        return reply
    except Exception as e:
        return f"Error communicating with LLM, Sir: {str(e)}"

def summarize(text: str) -> str:
    """
    Summarize the given text using the LLM.
    """
    if not api_key:
        return "No API key set, Sir. Please set your OpenRouter API key first."

    prompt = f"Please summarize the following text concisely:\n\n{text}"

    try:
        client = openai.OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"Error summarizing text, Sir: {str(e)}"
