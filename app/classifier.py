import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables (gets API key from .env)
load_dotenv()


class NewsClassifier:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None

        # Valid categories as per requirements
        self.categories = [
            "Cybersecurity",
            "Artificial Intelligence & Emerging Tech",
            "Software & Development",
            "Hardware & Devices",
            "Tech Industry & Business",
            "Other",
        ]

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("NewsClassifier initialized in REAL AI mode.")
            except ImportError:
                print(
                    "OpenAI package not found. Please install it with `pip install openai`."
                )
        else:
            print("No OPENAI_API_KEY found. NewsClassifier initialized in MOCK mode.")

    def classify(self, text: str) -> str:
        """
        Classifies the given text into one of the predefined categories.
        """
        if not text:
            return "Other"

        # Trying AI Mode
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"You are a tech news classifier. Classify the given news title/summary "
                                f"into exactly one of these categories: {', '.join(self.categories)}. "
                                "Return ONLY the category name. Do not add punctuation or explanations."
                            ),
                        },
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3,  # Low temperature for consistent categorization (Maybe Experiment with it later)
                    max_tokens=20,
                )
                category = response.choices[0].message.content.strip()

                # Basic validation to ensure LLM didn't hallucinate a new category
                if category in self.categories:
                    return category
                else:
                    print(
                        f"LLM returned invalid category: {category}. Defaulting to 'Other'."
                    )
                    return "Other"

            except Exception as e:
                print(f"LLM Classification failed: {e}. Falling back to keyword match.")

        # 2. Mock Mode (Fallback logic to work without API key and if LLM fails)
        text_lower = text.lower()
        if any(x in text_lower for x in ["security", "hack", "breach", "malware"]):
            return "Cybersecurity"
        elif any(x in text_lower for x in ["ai ", "gpt", "llm", "neural", "robot"]):
            return "Artificial Intelligence & Emerging Tech"
        elif any(
            x in text_lower for x in ["python", "code", "programming", "dev", "git"]
        ):
            return "Software & Development"
        elif any(
            x in text_lower
            for x in ["chip", "intel", "amd", "nvidia", "phone", "laptop"]
        ):
            return "Hardware & Devices"
        elif any(x in text_lower for x in ["stock", "market", "acquisition", "ceo"]):
            return "Tech Industry & Business"

        return "Other"


# --- Test Block ---
if __name__ == "__main__":
    classifier = NewsClassifier()

    test_headlines = [
        "Nvidia reveals new RTX 5090 graphics card",
        "OpenAI releases GPT-5 with advanced reasoning",
        "Python 3.14 adds new pattern matching features",
    ]

    print("\n--- CLASSIFICATION TEST ---")
    for headline in test_headlines:
        category = classifier.classify(headline)
        print(f"Title: {headline}\n -> Category: {category}\n")
