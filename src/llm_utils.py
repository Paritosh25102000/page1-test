"""
LLM utilities for trade type classification.

Provides a cascading LLM wrapper with rate-limited API key rotation:
1. First 15 calls/minute: Primary Google Gemini API key
2. Calls 16-30/minute: Secondary Google Gemini API key
3. 30+ calls/minute or fallback: OpenRouter API

All APIs use gemini-3-flash-preview with thinking level medium.
"""

import logging
import os
import time
from collections import deque
from pathlib import Path
from typing import List, Dict, Optional

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

# Rate limits per API key per minute (free tier: 5 RPM per key)
RATE_LIMIT_PER_KEY = 5
RATE_WINDOW_SECONDS = 60


class RateLimitTracker:
    """Tracks API calls within a sliding time window."""

    def __init__(self, window_seconds: int = RATE_WINDOW_SECONDS):
        self.window_seconds = window_seconds
        self.calls: deque = deque()

    def record_call(self):
        """Record a new API call."""
        self.calls.append(time.time())
        self._cleanup()

    def get_call_count(self) -> int:
        """Get the number of calls within the current window."""
        self._cleanup()
        return len(self.calls)

    def _cleanup(self):
        """Remove calls outside the time window."""
        cutoff = time.time() - self.window_seconds
        while self.calls and self.calls[0] < cutoff:
            self.calls.popleft()


class UniversalLLM:
    """
    Cascading LLM interface with rate-limited API key rotation.

    Uses Google Gemini API directly for first 30 calls/minute (split between 2 keys),
    then falls back to OpenRouter. All use gemini-3-flash-preview with thinking medium.
    """

    def __init__(self, api_key: str = None, model: str = "google/gemini-3-flash-preview"):
        """
        Initialize the LLM interface.

        Args:
            api_key: OpenRouter API key (for fallback)
            model: Model to use (default: google/gemini-3-flash-preview)
        """
        self.openrouter_api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not provided and not found in environment")

        # Load Gemini API keys from environment
        self.gemini_api_key_1 = os.getenv("GEMINI_API_KEY_1")
        self.gemini_api_key_2 = os.getenv("GEMINI_API_KEY_2")

        if not self.gemini_api_key_1 or not self.gemini_api_key_2:
            logger.warning("GEMINI_API_KEY_1 or GEMINI_API_KEY_2 not found in environment. Will use OpenRouter only.")

        self.model = model
        self.gemini_model = "gemini-3-flash-preview"
        self.base_url = "https://openrouter.ai/api/v1"

        # Rate tracking for each API key
        self.rate_tracker_1 = RateLimitTracker()
        self.rate_tracker_2 = RateLimitTracker()

        # Initialize Google Gemini client
        self.gemini_client = None
        try:
            from google import genai
            self.genai = genai
            self.gemini_available = True
            logger.info("Google Gemini SDK available")
        except ImportError:
            self.gemini_available = False
            logger.warning("google-genai package not installed. Install with: pip install google-genai")

        # Initialize OpenAI-compatible client for OpenRouter fallback
        try:
            from openai import OpenAI

            self.openrouter_client = OpenAI(
                base_url=self.base_url,
                api_key=self.openrouter_api_key,
            )
            logger.info(f"Initialized UniversalLLM with model: {self.model}")
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

    def _get_gemini_client(self, api_key: str):
        """Create a Gemini client with the specified API key."""
        return self.genai.Client(api_key=api_key)

    def _select_api(self) -> tuple[str, Optional[str], Optional[RateLimitTracker]]:
        """
        Select which API to use based on current rate limits.

        Returns:
            Tuple of (api_type, api_key, rate_tracker) where api_type is 'gemini' or 'openrouter'
        """
        # Check if Gemini keys are available
        if not self.gemini_api_key_1 or not self.gemini_api_key_2:
            return ('openrouter', None, None)

        count_1 = self.rate_tracker_1.get_call_count()
        count_2 = self.rate_tracker_2.get_call_count()

        if count_1 < RATE_LIMIT_PER_KEY:
            logger.debug(f"Using Gemini API key 1 (calls this minute: {count_1})")
            return ('gemini', self.gemini_api_key_1, self.rate_tracker_1)
        elif count_2 < RATE_LIMIT_PER_KEY:
            logger.debug(f"Using Gemini API key 2 (calls this minute: {count_2})")
            return ('gemini', self.gemini_api_key_2, self.rate_tracker_2)
        else:
            logger.debug(f"Rate limits exceeded (key1: {count_1}, key2: {count_2}), using OpenRouter")
            return ('openrouter', None, None)

    async def _call_gemini(self, messages: List[Dict], api_key: str) -> str:
        """
        Call Google Gemini API directly with thinking mode.

        Args:
            messages: List of message dictionaries
            api_key: Google API key to use

        Returns:
            Response content string
        """
        from google.genai import types

        client = self._get_gemini_client(api_key)

        # Convert messages to Gemini format
        # Gemini expects a simple content string or list of content parts
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Map roles: system -> user (prepended), assistant -> model
            if role == "system":
                contents.insert(0, types.Content(
                    role="user",
                    parts=[types.Part(text=f"[System Instructions]: {content}")]
                ))
            elif role == "assistant":
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=content)]
                ))
            else:  # user
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=content)]
                ))

        # Configure thinking mode with medium level
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="medium"
            ),
            temperature=0.2,
        )

        response = client.models.generate_content(
            model=self.gemini_model,
            contents=contents,
            config=config,
        )

        # Extract the non-thought response text
        result_text = ""
        for part in response.candidates[0].content.parts:
            if not getattr(part, 'thought', False):
                result_text += part.text

        return result_text

    async def _call_openrouter(self, messages: List[Dict]) -> str:
        """
        Call OpenRouter API as fallback.

        Args:
            messages: List of message dictionaries

        Returns:
            Response content string
        """
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            openai_messages.append({"role": role, "content": content})

        response = self.openrouter_client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.2,
        )

        return response.choices[0].message.content

    async def ainvoke(self, messages: List[Dict]) -> "AIMessage":
        """
        Async invoke the LLM with cascading API selection.

        Args:
            messages: List of message dictionaries with "role" and "content"

        Returns:
            AIMessage with response content
        """
        try:
            # Select API based on rate limits
            api_type, api_key, rate_tracker = self._select_api()

            if api_type == 'gemini' and self.gemini_available:
                try:
                    # Record the call before making it
                    rate_tracker.record_call()

                    content = await self._call_gemini(messages, api_key)
                    logger.debug(f"Gemini response received: {len(content)} characters")
                    return AIMessage(content=content)

                except Exception as e:
                    logger.warning(f"Gemini API call failed: {e}, falling back to OpenRouter")
                    # Fall through to OpenRouter

            # Fallback to OpenRouter
            content = await self._call_openrouter(messages)
            logger.debug(f"OpenRouter response received: {len(content)} characters")
            return AIMessage(content=content)

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise


class AIMessage:
    """Simple message container for LLM responses."""

    def __init__(self, content: str):
        self.content = content
