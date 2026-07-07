"""
Intent detection for the offline nutrition chatbot.

Uses lightweight NLP preprocessing (lowercasing, punctuation stripping,
tokenisation, tiny stop-word removal) followed by ordered keyword / phrase
matching. No external NLP library or network access is required.

`detect_intent()` also handles follow-up questions: a bare "why?" resolves
against the previous intent stored in the conversation context.
"""
from __future__ import annotations

import re
from typing import Optional

from .knowledge_base import find_additive_codes

# Intent name constants (avoids typos across the codebase)
GREETING              = "greeting"
CAN_I_EAT             = "can_i_eat"
WHY                   = "why"
IS_HEALTHY            = "is_healthy"
IS_SAFE               = "is_safe"
CONTAINS_GLUTEN       = "contains_gluten"
CONTAINS_DAIRY        = "contains_dairy"
CONTAINS_NUTS         = "contains_nuts"
CONTAINS_SOY          = "contains_soy"
CONTAINS_EGG          = "contains_egg"
IS_VEGAN              = "is_vegan"
IS_VEGETARIAN         = "is_vegetarian"
HIGH_SUGAR            = "high_sugar"
HIGH_SODIUM           = "high_sodium"
WHY_AVOID             = "why_avoid"
WHY_SAFE              = "why_safe"
DANGEROUS_INGREDIENT  = "dangerous_ingredient"
EXPLAIN_INGREDIENTS   = "explain_ingredients"
WHAT_IS_ADDITIVE      = "what_is_additive"
WHAT_PRESERVATIVES    = "what_preservatives"
ALTERNATIVES          = "alternatives"
GOOD_FOR_DIABETES     = "good_for_diabetes"
GOOD_FOR_BP           = "good_for_bp"
GOOD_FOR_HEART        = "good_for_heart"
GOOD_FOR_KIDNEY       = "good_for_kidney"
GOOD_FOR_LACTOSE      = "good_for_lactose"
GOOD_FOR_CELIAC       = "good_for_celiac"
SUMMARIZE             = "summarize"
RECOMMENDATION        = "recommendation"
UNKNOWN               = "unknown"

_STOPWORDS = {
    "the", "a", "an", "is", "are", "this", "that", "it", "of", "to", "for",
    "do", "does", "can", "could", "would", "should", "i", "me", "my", "please",
    "and", "or", "in", "on", "with", "have", "has", "am",
}


def preprocess(message: str) -> tuple[str, list[str]]:
    """
    Return (clean_text, tokens).

    clean_text keeps the normalised sentence for phrase matching.
    tokens is a stop-word-filtered token list for keyword matching.
    """
    text = (message or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)      # keep alphanum + hyphen
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [t for t in text.split(" ") if t and t not in _STOPWORDS]
    return text, tokens


def _has_any(text: str, phrases: list[str]) -> bool:
    return any(p in text for p in phrases)


def detect_intent(message: str, last_intent: Optional[str] = None,
                  last_rating: Optional[str] = None) -> tuple[str, dict]:
    """
    Classify *message* into an intent.

    Parameters
    ----------
    message      : raw user message
    last_intent  : the previous turn's intent (for follow-ups like "why?")
    last_rating  : the previous product rating ("safe"/"caution"/"avoid"),
                   used to resolve a bare "why?" into why_safe / why_avoid.

    Returns
    -------
    (intent_name, entities)  where entities may hold {"additive": "e471"} etc.
    """
    text, tokens = preprocess(message)
    entities: dict = {}

    if not text:
        return UNKNOWN, entities

    # ── E-number / additive lookup (high priority, very specific) ──────────
    codes = find_additive_codes(text)
    if codes:
        entities["additive"] = codes[0]
        return WHAT_IS_ADDITIVE, entities
    if _has_any(text, ["what does", "what is"]) and _has_any(text, ["mean", "e4", "e5", "e2", "e1", "additive"]):
        return WHAT_IS_ADDITIVE, entities

    # ── Greetings ──────────────────────────────────────────────────────────
    if _has_any(text, ["hello", "hi ", "hey", "namaste"]) or text in ("hi", "hey", "hello"):
        return GREETING, entities

    # ── "why" family (specific before generic) ─────────────────────────────
    if _has_any(text, ["why avoid", "why should i avoid", "why not", "why is it bad", "why bad"]):
        return WHY_AVOID, entities
    if _has_any(text, ["why safe", "why is it safe", "why is it good", "why ok"]):
        return WHY_SAFE, entities

    # Bare "why?" — resolve against previous turn
    if text in ("why", "why though", "how come", "explain why") or (tokens == ["why"]):
        if last_rating == "safe":
            return WHY_SAFE, entities
        if last_rating in ("avoid", "caution"):
            return WHY_AVOID, entities
        # fall back to generic explanation of the last topic
        return WHY, entities

    # ── Alternatives / recommendations ─────────────────────────────────────
    if _has_any(text, ["alternative", "healthier option", "instead", "substitute",
                        "similar product", "other option"]):
        return ALTERNATIVES, entities
    if _has_any(text, ["recommend", "recommendation", "your advice", "advise",
                        "what should i do", "what do you suggest"]):
        return RECOMMENDATION, entities

    # ── Contains-X questions (before generic health) ───────────────────────
    if _has_any(text, ["gluten", "wheat"]) and _has_any(text, ["contain", "have", "has", "any", "free", "got"]):
        return CONTAINS_GLUTEN, entities
    if "gluten" in text and last_intent is None:
        return CONTAINS_GLUTEN, entities
    if _has_any(text, ["dairy", "milk", "lactose"]) and _has_any(text, ["contain", "have", "has", "any", "free", "got"]):
        return CONTAINS_DAIRY, entities
    if _has_any(text, ["nut", "peanut"]) and _has_any(text, ["contain", "have", "has", "any", "free", "got"]):
        return CONTAINS_NUTS, entities
    if "soy" in text and _has_any(text, ["contain", "have", "has", "any", "free", "got"]):
        return CONTAINS_SOY, entities
    if "egg" in text and _has_any(text, ["contain", "have", "has", "any", "free", "got"]):
        return CONTAINS_EGG, entities

    # ── Diet suitability ────────────────────────────────────────────────────
    if "vegan" in text:
        return IS_VEGAN, entities
    if _has_any(text, ["vegetarian", "veg friendly"]) or tokens[:1] == ["veg"]:
        return IS_VEGETARIAN, entities

    # ── Condition-specific "good for" questions ─────────────────────────────
    if _has_any(text, ["diabet", "blood sugar", "glucose"]):
        return GOOD_FOR_DIABETES, entities
    if _has_any(text, ["blood pressure", "hypertension", " bp", "bp "]) or text == "bp":
        return GOOD_FOR_BP, entities
    if _has_any(text, ["heart", "cardiac", "cardiovascular", "cholesterol"]):
        return GOOD_FOR_HEART, entities
    if _has_any(text, ["kidney", "renal"]):
        return GOOD_FOR_KIDNEY, entities
    if _has_any(text, ["lactose intoler", "lactose"]):
        return GOOD_FOR_LACTOSE, entities
    if _has_any(text, ["celiac", "coeliac"]):
        return GOOD_FOR_CELIAC, entities

    # ── Nutrient level questions ─────────────────────────────────────────────
    if _has_any(text, ["high in sugar", "too much sugar", "sugar level", "how much sugar", "sugary", "sweet"]) or "sugar" in text:
        return HIGH_SUGAR, entities
    if _has_any(text, ["high in sodium", "too much salt", "sodium level", "salty", "sodium", "salt"]):
        return HIGH_SODIUM, entities

    # ── Ingredient explanation / danger ──────────────────────────────────────
    if _has_any(text, ["dangerous", "harmful", "which ingredient", "bad ingredient", "worst ingredient"]):
        return DANGEROUS_INGREDIENT, entities
    if _has_any(text, ["preservative"]):
        return WHAT_PRESERVATIVES, entities
    if _has_any(text, ["explain ingredient", "explain the ingredient", "ingredients", "what ingredients", "break down"]):
        return EXPLAIN_INGREDIENTS, entities

    # ── Summary / overview ────────────────────────────────────────────────────
    if _has_any(text, ["summarize", "summarise", "summary", "overview", "tell me about", "describe"]):
        return SUMMARIZE, entities

    # ── Health / safety / eat questions (generic, lower priority) ─────────────
    if _has_any(text, ["can i eat", "should i eat", "can i have", "safe to eat",
                       "okay to eat", "ok to eat", "eat this", "consume this"]):
        return CAN_I_EAT, entities
    if _has_any(text, ["is it healthy", "healthy", "nutritious", "good for me"]):
        return IS_HEALTHY, entities
    if _has_any(text, ["is it safe", "safe", "is this ok", "is it ok", "is it fine"]):
        return IS_SAFE, entities

    return UNKNOWN, entities
