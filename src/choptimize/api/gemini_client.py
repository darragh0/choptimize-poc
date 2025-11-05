"""Gemini API client for prompt analysis.

This module handles all interactions with the Google Gemini API.
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from choptimize.analysis.criteria import SYSTEM_INSTRUCTIONS
from choptimize.types import GeminiConfig


class GeminiClientError(Exception):
    """Raised when there's an error communicating with Gemini API."""


def _parse_json_response(response_text: str) -> dict[str, Any]:
    """Parse JSON response from Gemini.

    Args:
        response_text: The response text from Gemini.

    Returns:
        Parsed JSON dictionary.

    Raises:
        GeminiClientError: If JSON parsing fails.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise GeminiClientError(
            f"Failed to parse Gemini response as JSON: {e}\nResponse: {response_text}"
        ) from e


def _get_generation_config(system_instruction: str) -> types.GenerateContentConfig:
    """Create generation config with system instruction.

    Args:
        system_instruction: System instruction to include in config.

    Returns:
        GenerateContentConfig with all parameters configured.
    """
    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,  # Lower temperature for more consistent analysis
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )


def _get_api_key() -> str:
    """Load API key from environment variables.

    Returns:
        The Gemini API key.

    Raises:
        KeyError: If API key not found in environment.
    """
    env_path = Path.cwd() / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key is None:
        raise KeyError(
            "GEMINI_API_KEY not found in environment variables\n"
            "please create a `.env` file with your API key"
        )

    return api_key


def create_gemini_config() -> GeminiConfig:
    """Create Gemini configuration with API key from environment.

    Returns:
        GeminiConfig with initialized client.

    Raises:
        KeyError: If API key not found in environment.
    """
    api_key = _get_api_key()
    client = genai.Client(api_key=api_key)
    return GeminiConfig(client=client)


def analyze_prompt(config: GeminiConfig, prompt_text: str) -> dict[str, Any]:
    """Analyze coding prompt with Gemini.

    Args:
        config: Gemini configuration.
        prompt_text: Prompt to send to Gemini for analysis.

    Returns:
        A dictionary containing analysis results.

    Raises:
        GeminiClientError: If error communicating with API.
    """

    try:
        gen_config = _get_generation_config(SYSTEM_INSTRUCTIONS)
        response = config.client.models.generate_content(
            model=config.model_name,
            contents=prompt_text,
            config=gen_config,
        )
        if response.text is None:
            raise Exception("No response from Gemini API")
        return _parse_json_response(response.text)
    except Exception as e:
        raise GeminiClientError(f"Error calling Gemini API: {e}") from e
