"""
Prompt builder for the Phi-3 nutrition analysis engine.

Constructs a single, compact prompt that combines:
  1. A strict system instruction (behaviour + JSON format contract)
  2. The user's health profile
  3. The scanned product's nutritional data
  4. Retrieved RAG context (up to 4 knowledge-base snippets)

Design goals
------------
- Keep total prompt under ~1200 tokens so Phi-3 (2.2 GB) can fit it in context.
- Use structured delimiters so the model can clearly separate sections.
- Enforce JSON output via explicit format instructions and an example skeleton.
"""
from __future__ import annotations

from typing import Optional


SYSTEM_INSTRUCTION = """\
You are a friendly, balanced nutrition assistant — like a knowledgeable friend who gives honest but realistic advice. You are NOT a strict health enforcer.

IMPORTANT TONE RULES:
- Be realistic. Most foods are fine occasionally — say so.
- Never treat a single food as poison unless it literally is dangerous (e.g. contains a confirmed allergen for this user).
- Acknowledge that treats, snacks, and indulgent foods have a place in a balanced diet.
- Use phrases like "fine occasionally", "enjoy in moderation", "not an everyday food", "a treat rather than a staple".
- Only use strong warnings for things that DIRECTLY conflict with the user's specific conditions or allergies.
- Do NOT lecture or moralize. Give facts, not judgment.
- A score of 0 or 100 is almost never realistic. Most foods score 30-75.
- health_rating "Avoid" should ONLY be used if the product contains a confirmed allergen for this user or directly contradicts a severe medical condition.

SCORING GUIDE:
- 70-100: Nutritious everyday food (whole grains, fruits, vegetables, lean protein)
- 50-69: Acceptable, fine in moderation (most snacks, processed foods)
- 30-49: Not ideal nutritionally, limit intake (sugary drinks, chips, fast food)
- 10-29: Only for very specific medical conflicts (contains user's allergen, extreme sugar for diabetic)
- "Avoid" rating: ONLY if user's specific allergen is present

REQUIRED JSON FORMAT — respond with ONLY this JSON, nothing else:
{"overall_score":0,"health_rating":"","summary":"","pros":[],"cons":[],"warnings":[],"recommended_for":[],"avoid_if":[],"better_alternatives":[],"daily_limit":"","personalized_advice":"","confidence":0.0}

Keep all strings under 20 words. Max 3 items per list. Be warm, honest, and realistic."""


def build_prompt(
    product: object,
    profile: Optional[object],
    rag_context: list[str],
) -> tuple[str, str]:
    """
    Construct the system and user prompt for Phi-3.

    Returns
    -------
    (system_prompt, user_prompt) — passed separately to ollama_client.generate()
    """
    user_prompt = _product_section(product) + _profile_section(profile) + _rag_section(rag_context)
    user_prompt += "\n\nAnalyze this product honestly and realistically. Most foods are fine occasionally — reflect that. Return ONLY the JSON."
    return SYSTEM_INSTRUCTION, user_prompt


def build_rag_query(product: object, profile: Optional[object]) -> str:
    """
    Build a concise query string used to retrieve relevant RAG documents.
    Combines product name, category, key ingredients, and user conditions.
    """
    parts: list[str] = []

    # Product signals
    name = getattr(product, "name", "") or ""
    category = getattr(product, "category", "") or ""
    ingredients = (getattr(product, "ingredients_text", "") or "")[:300]
    additives = " ".join(getattr(product, "additives", []) or [])[:100]
    allergens = " ".join(getattr(product, "allergens", []) or [])[:100]

    if name:       parts.append(name)
    if category:   parts.append(category)
    if ingredients: parts.append(ingredients)
    if additives:  parts.append(f"additives: {additives}")
    if allergens:  parts.append(f"allergens: {allergens}")

    # User condition signals
    if profile:
        conditions = " ".join(getattr(profile, "health_conditions", []) or [])
        allergies  = " ".join(getattr(profile, "allergies", []) or [])
        diet       = getattr(profile, "diet_preference", "") or ""
        if conditions: parts.append(f"user conditions: {conditions}")
        if allergies:  parts.append(f"user allergies: {allergies}")
        if diet:       parts.append(f"diet: {diet}")

    return ". ".join(parts)


# ── Private helpers ──────────────────────────────────────────────────────────

def _product_section(product: object) -> str:
    nutrition = getattr(product, "nutrition_per_100g", {}) or {}
    allergens  = ", ".join(getattr(product, "allergens", []) or []) or "None listed"
    additives  = ", ".join(getattr(product, "additives", []) or []) or "None listed"
    nova       = getattr(product, "nova_group", None)
    nova_str   = f"{nova} (1=minimal processing, 4=ultra-processed)" if nova else "Unknown"

    lines = [
        "=== PRODUCT DATA ===",
        f"Name:          {getattr(product, 'name', 'Unknown')}",
        f"Brand:         {getattr(product, 'brand', 'Unknown') or 'Unknown'}",
        f"Category:      {getattr(product, 'category', 'Unknown') or 'Unknown'}",
        f"Nutriscore:    {(getattr(product, 'nutriscore_grade', '') or 'N/A').upper()}",
        f"NOVA group:    {nova_str}",
        f"Vegan:         {getattr(product, 'is_vegan', False)}",
        f"Vegetarian:    {getattr(product, 'is_vegetarian', False)}",
        f"Allergens:     {allergens}",
        f"Additives:     {additives}",
    ]

    # Ingredients (truncated to keep prompt short)
    ing = (getattr(product, "ingredients_text", "") or "").strip()
    if ing:
        lines.append(f"Ingredients:   {ing[:250]}{'...' if len(ing) > 250 else ''}")

    # Nutrition facts
    if nutrition:
        lines.append("Nutrition/100g:")
        nmap = {
            "energy_kcal":      "  Energy (kcal)",
            "proteins_g":       "  Protein (g)",
            "carbohydrates_g":  "  Carbs (g)",
            "sugars_g":         "  Sugars (g)",
            "fat_g":            "  Fat (g)",
            "saturated_fat_g":  "  Saturated fat (g)",
            "fiber_g":          "  Fibre (g)",
            "sodium_mg":        "  Sodium (mg)",
            "salt_g":           "  Salt (g)",
        }
        for key, label in nmap.items():
            val = nutrition.get(key)
            if val is not None:
                lines.append(f"{label}: {val}")

    return "\n".join(lines)


def _profile_section(profile) -> str:
    if profile is None:
        return "\n\n=== USER PROFILE ===\nNo profile available. Provide general analysis."

    bmi = getattr(profile, "bmi", None)
    conditions = ", ".join(getattr(profile, "health_conditions", []) or []) or "None"
    allergies  = ", ".join(getattr(profile, "allergies", []) or []) or "None"
    diet       = getattr(profile, "diet_preference", "No preference") or "No preference"
    goals      = ", ".join(getattr(profile, "goals", []) or []) or "Not specified"
    # Extended profile fields (may not exist on older profiles)
    activity   = getattr(profile, "activity_level", None) or "Not specified"
    calories   = getattr(profile, "daily_calorie_target", None)
    fitness    = getattr(profile, "fitness_goal", None) or "Not specified"

    lines = [
        "\n\n=== USER PROFILE ===",
        f"Age:               {getattr(profile, 'age', 'N/A')}",
        f"Gender:            {getattr(profile, 'gender', 'N/A')}",
        f"Weight:            {getattr(profile, 'weight_kg', 'N/A')} kg",
        f"Height:            {getattr(profile, 'height_cm', 'N/A')} cm",
        f"BMI:               {bmi or 'N/A'}",
        f"Activity level:    {activity}",
        f"Fitness goal:      {fitness}",
        f"Diet preference:   {diet}",
        f"Health conditions: {conditions}",
        f"Allergies:         {allergies}",
        f"Goals:             {goals}",
    ]
    if calories:
        lines.append(f"Daily calorie target: {calories} kcal")

    return "\n".join(lines)


def _rag_section(rag_context: list[str]) -> str:
    if not rag_context:
        return ""
    # Limit each snippet to 200 chars to keep prompt compact
    snippets = [doc[:200] for doc in rag_context[:3]]
    numbered = "\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(snippets))
    return f"\n\n=== NUTRITION KNOWLEDGE ===\n{numbered}"
