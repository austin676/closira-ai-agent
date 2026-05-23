import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env
load_dotenv()

# Lazy-loaded singleton client
_client = None


def get_client() -> genai.Client:
    """
    Lazily initializes and returns the Gemini client.

    Raises:
        ValueError: If GEMINI_API_KEY is missing.
    """
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Please configure it in a .env file."
            )

        _client = genai.Client(api_key=api_key)

    return _client


def send_chat(
    messages: List[Dict[str, Any]],
    model: str = "gemini-2.5-flash",
    **kwargs: Any,
) -> str:
    """
    Sends a chat request to Gemini and returns the response text.

    Internally converts OpenAI-style message format into
    a Gemini-compatible prompt string.

    Args:
        messages:
            Example:
            [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."}
            ]

        model:
            Gemini model name.

        **kwargs:
            Supports OpenAI-style response_format translation.

    Returns:
        Model response text.
    """

    client = get_client()

    system_instruction = None
    prompt_parts = []

    # Convert OpenAI-style messages into Gemini format
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")

        if role == "system":
            system_instruction = content
        else:
            prompt_parts.append(content)

    # Merge all non-system messages into one prompt
    prompt_string = "\n".join(prompt_parts)

    # Optional JSON output mode
    response_mime_type = None

    if "response_format" in kwargs:
        response_format = kwargs["response_format"]

        if (
            isinstance(response_format, dict)
            and response_format.get("type") == "json_object"
        ):
            response_mime_type = "application/json"

    # Gemini generation config
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type=response_mime_type,
    )

    # Standard non-streaming request
    response = client.models.generate_content(
        model=model,
        contents=prompt_string,
        config=config,
    )

    return response.text


def send_chat_request(messages: List[Dict[str, Any]]) -> str:
    """
    Convenience wrapper used by services.

    Args:
        messages: OpenAI-style message list.

    Returns:
        Model response text.
    """
    return send_chat(messages)