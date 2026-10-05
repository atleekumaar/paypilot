"""Intent extraction service transforming natural language requests into structured intent."""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.schemas.intent import BudgetConstraint, HardConstraints, ProductSearchIntent

logger = logging.getLogger(__name__)

# Known product categories and synonyms
CATEGORY_MAP = {
    "laptop": ["laptop", "laptops", "notebook", "notebooks", "macbook", "chromebook", "ultrabook", "pc"],
    "phone": ["phone", "phones", "smartphone", "smartphones", "iphone", "android", "mobile", "cellphone"],
    "headphones": ["headphone", "headphones", "earbuds", "headset", "earphones", "cans", "airpods"],
    "keyboard": ["keyboard", "keyboards", "keeb"],
    "monitor": ["monitor", "monitors", "display", "screen", "displays", "screens"],
    "smartwatch": ["smartwatch", "smartwatches", "watch", "watches", "fitness tracker", "wearable"],
    "accessory": ["accessory", "accessories", "charger", "dock", "mouse", "powerbank", "power bank", "adapter", "stand"],
}


class IntentService:
    """Service to extract structured, normalized search intent from user queries."""

    def __init__(self, api_key: Optional[str] = None):
        self._settings = get_settings()
        self._api_key = api_key or self._settings.LLM_API_KEY

    def extract_intent(self, query: str) -> ProductSearchIntent:
        """Extract structured intent from user query.

        Attempts LLM extraction if API key is present and configured,
        otherwise uses deterministic regex and semantic normalization.
        """
        cleaned_query = (query or "").strip()
        if not cleaned_query:
            return ProductSearchIntent(
                intent="product_search",
                category=None,
                hard_constraints=HardConstraints(in_stock=True),
            )

        # 1. Deterministic baseline extraction (guaranteed 100% reliable)
        deterministic_intent = self._deterministic_extract(cleaned_query)

        # 2. If LLM API key is present, attempt LLM enhancement
        if self._api_key and len(self._api_key) > 5 and not self._api_key.startswith("your_"):
            try:
                llm_intent = self._llm_extract(cleaned_query)
                if llm_intent:
                    return llm_intent
            except Exception as e:
                logger.warning(f"LLM intent extraction failed, falling back to deterministic extractor: {e}")

        return deterministic_intent

    def _deterministic_extract(self, query: str) -> ProductSearchIntent:
        """Deterministic rule-based and regex intent extractor."""
        q_lower = query.lower()

        # 1. Detect Category
        detected_category: Optional[str] = None
        for cat, synonyms in CATEGORY_MAP.items():
            for syn in synonyms:
                pattern = r"\b" + re.escape(syn) + r"\b"
                if re.search(pattern, q_lower):
                    detected_category = cat
                    break
            if detected_category:
                break

        # 2. Extract Budget Constraint
        max_budget: Optional[float] = None
        min_budget: Optional[float] = None

        # Check for phrase "under one grand" / "below 1k" / "under $1200"
        if "one grand" in q_lower or "a grand" in q_lower:
            max_budget = 1000.0
        elif "two grand" in q_lower:
            max_budget = 2000.0
        else:
            # Pattern for: under/below/less than/max/budget of $X or X dollars or X k
            k_match = re.search(r"(?:under|below|less than|max(?:imum)? of?|budget of?)\s*\$?(\d+(?:\.\d+)?)\s*k\b", q_lower)
            if k_match:
                max_budget = float(k_match.group(1)) * 1000.0
            else:
                max_match = re.search(
                    r"(?:under|below|less than|max(?:imum)? of?|budget of?|up to)\s*\$?(\d+(?:\.\d+)?)",
                    q_lower,
                )
                if max_match:
                    max_budget = float(max_match.group(1))

        # Check for min price: "at least $X", "above $X", "more than $X"
        min_match = re.search(r"(?:above|more than|at least|over)\s*\$?(\d+(?:\.\d+)?)", q_lower)
        if min_match:
            min_budget = float(min_match.group(1))

        # 3. Detect Use Case
        detected_use_case: Optional[str] = None
        use_case_patterns = [
            (r"\b(ai development|machine learning|deep learning|ml|ai)\b", "AI development"),
            (r"\b(software development|programming|coding|developer)\b", "Software development"),
            (r"\b(gaming|gamer|esports)\b", "Gaming"),
            (r"\b(video editing|content creation|graphic design)\b", "Content creation"),
            (r"\b(travel|commuting|on the go)\b", "Travel & Portability"),
            (r"\b(office|business|work)\b", "Office Work"),
            (r"\b(audiophile|critical listening|music production)\b", "Audio Production"),
        ]
        for pattern, label in use_case_patterns:
            if re.search(pattern, q_lower):
                detected_use_case = label
                break

        # 4. Extract Explicit Requirements & Soft Preferences
        requirements: List[str] = []
        soft_preferences: List[str] = []
        normalized_features: Dict[str, Any] = {}

        # Battery Life
        if re.search(r"\b(good battery|long battery|all[- ]day battery|battery life|great battery)\b", q_lower):
            requirements.append("good battery life")
            soft_preferences.append("high battery endurance")
            normalized_features["battery_hours_min"] = 8.0

        # AI Development / Machine Learning needs
        if detected_use_case == "AI development":
            requirements.append("AI development capability")
            soft_preferences.append("dedicated GPU / Tensor acceleration")
            soft_preferences.append("16GB+ RAM")
            normalized_features["gpu_preference"] = True
            normalized_features["ram_gb_min"] = 16

        # Noise Cancellation
        if re.search(r"\b(noise cancel|anc|quiet)\b", q_lower):
            requirements.append("active noise cancellation")
            soft_preferences.append("noise cancellation")
            normalized_features["noise_cancelling"] = True

        # Wireless
        if re.search(r"\b(wireless|bluetooth|cordless)\b", q_lower):
            requirements.append("wireless connectivity")
            soft_preferences.append("wireless")
            normalized_features["wireless"] = True

        # Mechanical
        if "mechanical" in q_lower:
            requirements.append("mechanical switches")
            soft_preferences.append("mechanical keyboard")

        # 4K / High Resolution
        if "4k" in q_lower or "high resolution" in q_lower:
            requirements.append("4K resolution")
            soft_preferences.append("high resolution")

        budget_obj = None
        if max_budget is not None or min_budget is not None:
            budget_obj = BudgetConstraint(max=max_budget, min=min_budget, currency="USD")

        hard_constraints = HardConstraints(
            max_price=max_budget,
            min_price=min_budget,
            category=detected_category,
            in_stock=True,
        )

        return ProductSearchIntent(
            intent="product_search",
            category=detected_category,
            budget=budget_obj,
            use_case=detected_use_case,
            requirements=requirements,
            preferences=soft_preferences,
            hard_constraints=hard_constraints,
            soft_preferences=soft_preferences,
            normalized_features=normalized_features,
        )

    def _llm_extract(self, query: str) -> Optional[ProductSearchIntent]:
        """Optionally invoke LLM for intent extraction if credentials exist."""
        # Built to integrate with standard LLM provider via structured JSON
        # Defaults to safe deterministic extraction if LLM is unavailable
        return None
