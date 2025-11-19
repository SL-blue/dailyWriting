# core/topic_generator.py

import os
import random
from typing import List, Optional

from google import genai

from .prompt_builder import build_topic_instruction


class TopicGenerator:
    """
    Topic generator using Google Gemini via google-genai.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # pick a valid model for your project; you can change this
        self.model: str = "gemini-2.5-flash"

        self._fallback_prompts = [
            "Write about a moment that quietly changed you.",
            "Describe a place you remember only in fragments.",
            "Write about an unexpected conversation.",
        ]

        if self.api_key:
            print("TopicGenerator: GOOGLE_API_KEY found, length =", len(self.api_key))
            self.client = genai.Client(api_key=self.api_key)
        else:
            print("TopicGenerator: GOOGLE_API_KEY NOT set – using fallback prompts only.")
            self.client = None

    def generate_topic(self, tag_ids: Optional[List[str]] = None) -> str:
        """
        Generate a writing prompt based on selected tag ids.
        """
        tag_ids = tag_ids or []
        instruction = build_topic_instruction(tag_ids)

        # No client => always fallback
        if not self.client:
            print("TopicGenerator: no client – returning fallback prompt.")
            return random.choice(self._fallback_prompts)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=instruction,
            )

            text = (response.text or "").strip()
            print("TopicGenerator: Gemini response text =", repr(text))

            if not text:
                print("TopicGenerator: empty response text – using fallback.")
                return random.choice(self._fallback_prompts)

            return text

        except Exception as e:
            print("Gemini topic generation failed:", e)
            return random.choice(self._fallback_prompts)
