"""
Core topic generator supporting Google Gemini and Anthropic Claude, with fallback prompts.
"""

import os
import random
import time
from typing import List, Optional

from .prompt_builder import build_topic_instruction
from .tags import TAG_REGISTRY
from .logging_config import get_logger
from .exceptions import TopicGenerationError

logger = get_logger("topic_generator")


class TopicGenerator:
    """
    Topic generator supporting multiple AI providers (Gemini and Claude).
    Falls back to predefined prompts if API keys are missing or errors occur.

    Attributes:
        provider: The AI provider to use ("gemini" or "claude").
        gemini_model: The Gemini model to use.
        claude_model: The Claude model to use.
        last_used_fallback: Indicates if the last topic was from fallback prompts.
        last_error: The last error message if fallback was used due to an error.
    """

    def __init__(self) -> None:
        self.provider: str = "gemini"
        self.gemini_model: str = "gemini-2.5-pro"
        self.claude_model: str = "claude-sonnet-4-6-20250514"

        self._fallback_prompts = [
            "Write about a moment that quietly changed you.",
            "Describe a place you remember only in fragments.",
            "Write about an unexpected conversation.",
        ]

        self.last_used_fallback: bool = False
        self.last_error: Optional[str] = None

        # Initialize API clients
        self._gemini_client = None
        self._claude_client = None

        # Check for Gemini API key
        self._gemini_api_key = os.getenv("GOOGLE_API_KEY")
        if self._gemini_api_key:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=self._gemini_api_key)
                logger.info("GOOGLE_API_KEY found (length=%d)", len(self._gemini_api_key))
            except ImportError:
                logger.warning("google-genai not installed")

        # Check for Claude API key
        self._claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if self._claude_api_key:
            try:
                import anthropic
                self._claude_client = anthropic.Anthropic(api_key=self._claude_api_key)
                logger.info("ANTHROPIC_API_KEY found (length=%d)", len(self._claude_api_key))
            except ImportError:
                logger.warning("anthropic not installed")

        if not self._gemini_api_key and not self._claude_api_key:
            logger.warning("No API keys set - using fallback prompts only")

    def set_provider(self, provider: str) -> None:
        """Set the AI provider to use."""
        if provider in ("gemini", "claude"):
            self.provider = provider
            logger.info("AI provider set to: %s", provider)
        else:
            logger.warning("Unknown provider: %s, keeping current: %s", provider, self.provider)

    def _get_active_client(self):
        """Get the active client based on provider setting."""
        if self.provider == "claude" and self._claude_client:
            return self._claude_client
        elif self.provider == "gemini" and self._gemini_client:
            return self._gemini_client
        # Fallback: try the other provider if primary isn't available
        elif self._claude_client:
            logger.info("Primary provider unavailable, falling back to Claude")
            return self._claude_client
        elif self._gemini_client:
            logger.info("Primary provider unavailable, falling back to Gemini")
            return self._gemini_client
        return None

    def generate_topic(self, tag_ids: Optional[List[str]] = None) -> str:
        """
        Generate a writing topic based on provided tag IDs.

        Args:
            tag_ids: Optional list of tag IDs to guide topic generation.

        Returns:
            A generated topic string.
        """
        self.last_used_fallback = False
        self.last_error = None

        user_tag_ids = tag_ids or []
        instruction = build_topic_instruction(user_tag_ids)

        client = self._get_active_client()
        if not client:
            logger.debug("No API client available - using fallback prompt")
            self.last_used_fallback = True
            self.last_error = "No API key configured"
            return random.choice(self._fallback_prompts)

        logger.info("Generating topic with %d tags using %s", len(user_tag_ids), self.provider)

        # Determine which provider to use based on client type
        if self._claude_client and client == self._claude_client:
            return self._generate_with_claude(instruction)
        else:
            return self._generate_with_gemini(instruction)

    def _generate_with_gemini(self, instruction: str) -> str:
        """Generate topic using Gemini API."""
        for attempt in range(3):
            try:
                response = self._gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=instruction,
                )
                text = (response.text or "").strip()

                if not text:
                    logger.warning("Empty response from Gemini - using fallback")
                    self.last_used_fallback = True
                    self.last_error = "Empty response from AI"
                    return random.choice(self._fallback_prompts)

                logger.info("Topic generated successfully with Gemini (%d chars)", len(text))
                return text

            except Exception as e:
                err_str = str(e)
                logger.warning("Gemini generation failed (attempt %d/3): %s", attempt + 1, err_str)

                # Retry only on 503/UNAVAILABLE
                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                    wait_time = 2.0 * (attempt + 1)
                    logger.info("Retrying in %.1f seconds...", wait_time)
                    time.sleep(wait_time)
                    continue

                self._set_error_from_exception(err_str)
                break

        # Try Claude as fallback if available
        if self._claude_client and self.provider == "gemini":
            logger.info("Gemini failed, trying Claude as fallback")
            return self._generate_with_claude(instruction)

        return self._return_fallback()

    def _generate_with_claude(self, instruction: str) -> str:
        """Generate topic using Claude API."""
        for attempt in range(3):
            try:
                message = self._claude_client.messages.create(
                    model=self.claude_model,
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": instruction}
                    ]
                )

                # Extract text from response
                text = ""
                for block in message.content:
                    if hasattr(block, "text"):
                        text += block.text

                text = text.strip()

                if not text:
                    logger.warning("Empty response from Claude - using fallback")
                    self.last_used_fallback = True
                    self.last_error = "Empty response from AI"
                    return random.choice(self._fallback_prompts)

                logger.info("Topic generated successfully with Claude (%d chars)", len(text))
                return text

            except Exception as e:
                err_str = str(e)
                logger.warning("Claude generation failed (attempt %d/3): %s", attempt + 1, err_str)

                # Retry on overloaded errors
                if ("overloaded" in err_str.lower() or "529" in err_str) and attempt < 2:
                    wait_time = 2.0 * (attempt + 1)
                    logger.info("Retrying in %.1f seconds...", wait_time)
                    time.sleep(wait_time)
                    continue

                self._set_error_from_exception(err_str)
                break

        # Try Gemini as fallback if available
        if self._gemini_client and self.provider == "claude":
            logger.info("Claude failed, trying Gemini as fallback")
            return self._generate_with_gemini(instruction)

        return self._return_fallback()

    def _set_error_from_exception(self, err_str: str) -> None:
        """Set last_error based on exception string."""
        if "API_KEY" in err_str or "401" in err_str or "authentication" in err_str.lower():
            self.last_error = "Invalid API key"
        elif "429" in err_str or "RATE" in err_str.upper() or "rate_limit" in err_str.lower():
            self.last_error = "Rate limit exceeded"
        elif "timeout" in err_str.lower():
            self.last_error = "Request timed out"
        elif "overloaded" in err_str.lower() or "529" in err_str:
            self.last_error = "Service overloaded"
        else:
            self.last_error = "API error occurred"

    def _return_fallback(self) -> str:
        """Return a fallback prompt."""
        logger.warning("All retries exhausted - using fallback prompt")
        self.last_used_fallback = True
        if not self.last_error:
            self.last_error = "Service temporarily unavailable"
        return random.choice(self._fallback_prompts)
