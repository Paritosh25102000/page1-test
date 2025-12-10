"""
LLM utilities for trade type classification.

Provides a simple UniversalLLM wrapper for OpenRouter API calls.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

# Load .env file if it exists
def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()


class UniversalLLM:
    """
    Simple LLM interface for OpenRouter API.
    """

    def __init__(self, api_key: str = None, model: str = "google/gemini-2.5-flash"):
        """
        Initialize the LLM interface.

        Args:
            api_key: OpenRouter API key
            model: Model to use (default: google/gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not provided and not found in environment")

        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"

        # Initialize OpenAI-compatible client
        try:
            from openai import OpenAI

            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
            logger.info(f"Initialized UniversalLLM with model: {self.model}")
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

    async def ainvoke(self, messages: List[Dict]) -> "AIMessage":
        """
        Async invoke the LLM.

        Args:
            messages: List of message dictionaries with "role" and "content"

        Returns:
            AIMessage with response content
        """
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            openai_messages.append({"role": role, "content": content})

        # Call API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=0.2,
            )

            # Extract content
            content = response.choices[0].message.content

            logger.debug(f"LLM response received: {len(content)} characters")

            return AIMessage(content=content)

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise


class AIMessage:
    """Simple message container for LLM responses."""

    def __init__(self, content: str):
        self.content = content
