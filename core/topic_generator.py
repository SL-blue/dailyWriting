"""
Core topic generator using Google Gemini via google-genai, with fallback prompts.
"""

import os
import random
import time
from typing import List, Optional

from google import genai

from .prompt_builder import build_topic_instruction
from .tags import TAG_REGISTRY
from .logging_config import get_logger
from .exceptions import TopicGenerationError

logger = get_logger("topic_generator")


class TopicGenerator:
    """
    Topic generator using Google Gemini via google-genai.
    Falls back to predefined prompts if API key is missing or errors occur.
    Attributes:
        api_key: The Google API key from environment variable.
        model: The Gemini model to use.
        last_used_fallback: Indicates if the last topic was from fallback prompts.
        last_error: The last error message if fallback was used due to an error.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model: str = "gemini-2.5-flash"

        self._fallback_prompts = [
            "Write about a moment that quietly changed you.",
            "Describe a place you remember only in fragments.",
            "Write about an unexpected conversation.",
        ]

        self.last_used_fallback: bool = False
        self.last_error: Optional[str] = None

        if self.api_key:
            logger.info("GOOGLE_API_KEY found (length=%d)", len(self.api_key))
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("GOOGLE_API_KEY not set - using fallback prompts only")
            self.client = None

    def generate_topic(self, tag_ids: Optional[List[str]] = None) -> str:
        """
        Generate a writing topic based on provided tag IDs.
        If no tag IDs are provided, uses fallback prompts.
        Args:
            tag_ids: Optional list of tag IDs to guide topic generation.
        Returns:
            A generated topic string.
        """
        self.last_used_fallback = False
        self.last_error = None

        user_tag_ids = tag_ids or []
        all_tag_ids = user_tag_ids
        instruction = build_topic_instruction(all_tag_ids)

        if not self.client:
            logger.debug("No API client - using fallback prompt")
            self.last_used_fallback = True
            self.last_error = "API key not configured"
            return random.choice(self._fallback_prompts)

        logger.info("Generating topic with %d tags", len(all_tag_ids))

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=instruction,
                )
                text = (response.text or "").strip()

                if not text:
                    logger.warning("Empty response from Gemini - using fallback")
                    self.last_used_fallback = True
                    self.last_error = "Empty response from AI"
                    return random.choice(self._fallback_prompts)

                logger.info("Topic generated successfully (%d chars)", len(text))
                return text

            except Exception as e:
                err_str = str(e)
                logger.warning("Topic generation failed (attempt %d/3): %s", attempt + 1, err_str)

                # Retry only on 503/UNAVAILABLE
                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                    wait_time = 2.0 * (attempt + 1)
                    logger.info("Retrying in %.1f seconds...", wait_time)
                    time.sleep(wait_time)
                    continue

                # Check for common error types
                if "API_KEY" in err_str or "401" in err_str:
                    self.last_error = "Invalid API key"
                elif "429" in err_str or "RATE" in err_str.upper():
                    self.last_error = "Rate limit exceeded"
                elif "timeout" in err_str.lower():
                    self.last_error = "Request timed out"
                else:
                    self.last_error = "API error occurred"

                break

        logger.warning("All retries exhausted - using fallback prompt")
        self.last_used_fallback = True
        if not self.last_error:
            self.last_error = "Service temporarily unavailable"
        return random.choice(self._fallback_prompts)
