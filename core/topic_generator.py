# core/topic_generator.py

import os
import random
import time
from typing import List, Optional

from google import genai

from .prompt_builder import build_topic_instruction
from .tags import TAG_REGISTRY


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

        self.last_used_fallback: bool = False 

        if self.api_key:
            print("TopicGenerator: GOOGLE_API_KEY found, length =", len(self.api_key))
            self.client = genai.Client(api_key=self.api_key)
        else:
            print("TopicGenerator: GOOGLE_API_KEY NOT set – using fallback prompts only.")
            self.client = None

    def generate_topic(self, tag_ids: Optional[List[str]] = None) -> str:
        self.last_used_fallback = False    # reset at start

        user_tag_ids = tag_ids or []

        # ... your hidden tag logic if any ...
        all_tag_ids = user_tag_ids

        instruction = build_topic_instruction(all_tag_ids)

        if not self.client:
            print("TopicGenerator: no client – returning fallback prompt.")
            self.last_used_fallback = True
            return random.choice(self._fallback_prompts)

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=instruction,
                )
                text = (response.text or "").strip()
                print("TopicGenerator: Gemini response text =", repr(text))

                if not text:
                    print("TopicGenerator: empty response text – using fallback.")
                    self.last_used_fallback = True
                    return random.choice(self._fallback_prompts)

                return text

            except Exception as e:
                err_str = str(e)
                print(f"Gemini topic generation failed (attempt {attempt+1}):", err_str)

                # Retry only on 503/UNAVAILABLE
                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                    time.sleep(2.0 * (attempt + 1))
                    continue

                # Other errors or exhausted retries → fallback
                break

        self.last_used_fallback = True
        return random.choice(self._fallback_prompts)
