# core/topic_generator.py

import os
import random
import requests


class TopicGenerator:
    def __init__(self):
        self._fallback_prompts = [
            "Describe a place that only exists in your memories.",
            "Write about a conversation you wish you had finished.",
            "Describe a day when everything felt slightly out of sync.",
            "Write a scene where two strangers share an unexpected moment of kindness.",
            "Describe a decision you made that quietly changed your life.",
        ]
        # Example: read key + endpoint from environment
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_url = os.getenv("LLM_API_URL")  # e.g. "https://.../v1/chat/completions"

    def generate_topic(self) -> str:
        # If no API configured, fall back gracefully
        if not self.api_key or not self.api_url:
            return random.choice(self._fallback_prompts)

        prompt = (
            "Generate a single creative writing prompt for a daily writing exercise. "
            "Return just the prompt sentence, no extra explanation."
        )

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "your-model-name-here",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            # This part depends on the provider’s response format;
            # adjust to match your API.
            topic_text = data["choices"][0]["message"]["content"].strip()
            return topic_text or random.choice(self._fallback_prompts)

        except Exception as e:
            # Log/print in real code; for now just fall back
            print("Topic generation failed:", e)
            return random.choice(self._fallback_prompts)
