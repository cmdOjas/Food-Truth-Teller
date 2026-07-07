"""
Hybrid response engine for the offline nutrition chatbot.

This is the orchestrator. It is deliberately decoupled from Flask and the
database: the caller passes in everything it needs (the analysed product,
the user profile, the rule-engine rating result, conversation history and
candidate products for alternatives, plus the rating function itself for
scoring alternatives). That keeps the engine pure and unit-testable.

The reply is produced by combining, per detected intent:
  • the user's health profile (conditions, allergies, diet, name)
  • the product's attributes and nutrition
  • the ingredient knowledge base
  • the rule-engine prediction (rating + reasons)
  • conversation context (for follow-ups like "why?")

No LLM, no external API, no network calls.
"""
from __future__ import annotations

from typing import Callable, Optional

from . import intents as I
from . import knowledge_base as KB

RATE_EMOJI = {"safe": "✅", "caution": "⚠️", "avoid": "🚫"}


# ──────────────────────────────────────────────────────────────────────────
# Small profile / product fact helpers
# ──────────────────────────────────────────────────────────────────────────
def _diseases(profile: dict) -> list[str]:
    return [d.lower() for d in (profile.get("diseases") or [])]


def _allergies(profile: dict) -> list[str]:
    return [a.lower() for a in (profile.get("allergies") or [])]


def _has_condition(profile: dict, *keys: str) -> bool:
    return any(k in d for k in keys for d in _diseases(profile))


def _has_allergy(profile: dict, *keys: str) -> bool:
    return any(k in a for k in keys for a in _allergies(profile))


def _sugar(product: dict) -> float:
    try:
        return float(product.get("per_100g_sugar") or 0)
    except (TypeError, ValueError):
        return 0.0


def _sodium(product: dict) -> float:
    try:
        return float(product.get("per_100g_sodium") or 0)
    except (TypeError, ValueError):
        return 0.0


def _name(product: dict) -> str:
    return product.get("product_name") or "this product"


def _ingredient_text(product: dict) -> str:
    return product.get("ingredients") or ""


# ──────────────────────────────────────────────────────────────────────────
# Per-intent response builders
# ──────────────────────────────────────────────────────────────────────────
def _reply_greeting(profile: dict, product: Optional[dict]) -> str:
    name = profile.get("name") or "there"
    conds = ", ".join(profile.get("diseases") or []) or "none on file"
    if product:
        return (f"Hi {name}! 👋 I'm your EatWise AI assistant. We're looking at "
                f"**{_name(product)}** right now. You can ask me things like "
                f"\"Can I eat this?\", \"Is it high in sugar?\" or \"Suggest a healthier alternative\".")
    return (f"Hi {name}! 👋 I'm your EatWise AI assistant.\n\n"
            f"Your health conditions on file: **{conds}**.\n"
            f"Scan a product and ask me anything about it.")


def _verdict_sentence(rating: str, product: dict) -> str:
    emoji = RATE_EMOJI.get(rating, "")
    if rating == "avoid":
        return f"{emoji} I'd recommend **avoiding {_name(product)}**."
    if rating == "caution":
        return f"{emoji} You can have **{_name(product)}** occasionally, but with **caution**."
    return f"{emoji} **{_name(product)}** looks **safe** for your profile."


def _reasons_block(reasons: list[str], limit: int = 4) -> str:
    picked = [r for r in reasons if not r.startswith("✅")][:limit]
    if not picked:
        picked = reasons[:limit]
    return "\n".join(f"• {r}" for r in picked)


def _reply_can_i_eat(profile, product, rating, reasons) -> str:
    verdict = _verdict_sentence(rating, product)
    body = _reasons_block(reasons)
    if rating == "safe":
        return f"{verdict}\n\nNothing in it conflicts with your health profile. Enjoy it as part of a balanced diet. 🌿"
    return f"{verdict}\n\nHere's why:\n{body}"


def _reply_is_healthy(profile, product, rating, reasons) -> str:
    sugar, sodium = _sugar(product), _sodium(product)
    lead = {
        "safe": "Overall this is a reasonable choice for you.",
        "caution": "It's okay in moderation, but not something to eat every day.",
        "avoid": "Honestly, this isn't a healthy pick for your profile.",
    }.get(rating, "")
    facts = []
    if sugar:
        facts.append(f"{sugar:.1f} g sugar/100 g")
    if sodium:
        facts.append(f"{sodium:.0f} mg sodium/100 g")
    facts_str = f" It has {' and '.join(facts)}." if facts else ""
    return f"{RATE_EMOJI.get(rating,'')} {lead}{facts_str}\n\n{_reasons_block(reasons)}"


def _reply_is_safe(profile, product, rating, reasons) -> str:
    return _reply_can_i_eat(profile, product, rating, reasons)


def _reply_why(profile, product, rating, reasons, positive: bool) -> str:
    if positive or rating == "safe":
        body = _reasons_block(reasons)
        return (f"It's a good fit because it stays within safe limits for your profile:\n{body}"
                if body else "It doesn't contain anything that conflicts with your health profile.")
    verdict = "caution" if rating == "caution" else "avoid"
    return (f"Here's the reasoning behind the **{verdict}** rating for **{_name(product)}**:\n"
            f"{_reasons_block(reasons)}")


def _reply_contains(profile, product, group_label, group_key) -> str:
    text = _ingredient_text(product)
    if not text:
        return (f"I don't have an ingredient list for **{_name(product)}**, so I can't "
                f"confirm whether it contains {group_label}. Please check the physical label.")
    present = KB.contains_group(text, group_key)
    if present:
        allergic = (
            (group_key == "gluten" and (_has_allergy(profile, "gluten") or _has_condition(profile, "celiac")))
            or (group_key == "dairy" and (_has_allergy(profile, "dairy") or _has_condition(profile, "lactose")))
            or (group_key == "nuts" and _has_allergy(profile, "nut", "peanut"))
            or (group_key == "soy" and _has_allergy(profile, "soy"))
            or (group_key == "egg" and _has_allergy(profile, "egg"))
        )
        warn = f" ⚠️ This matters for you — you've listed a {group_label} sensitivity, so I'd avoid it." if allergic else ""
        return f"Yes — **{_name(product)}** contains {group_label}.{warn}"
    return f"No — I don't see any {group_label} in the ingredients of **{_name(product)}**."


def _reply_is_vegan(profile, product) -> str:
    text = _ingredient_text(product)
    # Trust explicit product flag if present, else infer from ingredients
    flag = product.get("is_vegan")
    if flag is not None and str(flag) in ("1", "True", "true"):
        vegan = True
    elif flag is not None and str(flag) in ("0", "False", "false") and not text:
        vegan = False
    else:
        vegan = KB.is_probably_vegan(text) if text else bool(flag)
    if vegan:
        return f"🌱 Yes — **{_name(product)}** appears to be **vegan** (no animal-derived ingredients detected)."
    return (f"❌ No — **{_name(product)}** does **not** look vegan; it contains at least one "
            f"animal-derived ingredient (e.g. dairy, egg, gelatin or honey).")


def _reply_is_vegetarian(profile, product) -> str:
    text = _ingredient_text(product)
    flag = product.get("is_vegetarian")
    if flag is not None and str(flag) in ("1", "True", "true"):
        veg = True
    elif flag is not None and str(flag) in ("0", "False", "false") and not text:
        veg = False
    else:
        veg = KB.is_probably_vegetarian(text) if text else bool(flag)
    if veg:
        return f"🌿 Yes — **{_name(product)}** appears to be **vegetarian**."
    return (f"❌ No — **{_name(product)}** contains a non-vegetarian ingredient "
            f"(such as meat, fish, gelatin or rennet).")


def _reply_high_sugar(profile, product) -> str:
    sugar = _sugar(product)
    diabetic = _has_condition(profile, "diabetes")
    caution = 5.0 if diabetic else 10.0
    if sugar == 0:
        return f"**{_name(product)}** has no significant sugar listed (0 g/100 g)."
    level = "high" if sugar >= (caution * 2) else "elevated" if sugar >= caution else "moderate/low"
    note = ""
    if diabetic and sugar >= caution:
        note = " Since you're managing **diabetes**, I'd keep portions small or skip it."
    elif sugar >= caution * 2:
        note = " That's well above the general daily-limit guidance."
    return (f"**{_name(product)}** contains **{sugar:.1f} g of sugar per 100 g**, which is "
            f"{level}.{note}")


def _reply_high_sodium(profile, product) -> str:
    sodium = _sodium(product)
    sensitive = _has_condition(profile, "bp", "blood pressure", "hypertension", "kidney")
    caution = 200.0 if sensitive else 400.0
    if sodium == 0:
        return f"**{_name(product)}** has no significant sodium listed (0 mg/100 g)."
    level = "high" if sodium >= (caution * 2) else "elevated" if sodium >= caution else "moderate/low"
    note = ""
    if sensitive and sodium >= caution:
        note = " With your blood-pressure/kidney profile, high sodium is a real concern here."
    return (f"**{_name(product)}** contains **{sodium:.0f} mg of sodium per 100 g**, which is "
            f"{level}.{note}")


def _reply_dangerous_ingredient(profile, product) -> str:
    text = _ingredient_text(product)
    if not text:
        return f"I don't have an ingredient list for **{_name(product)}** to review."
    concerns: list[str] = []
    # Allergen concerns specific to the user
    for group, label in [("gluten", "gluten"), ("dairy", "dairy"), ("nuts", "nuts"),
                         ("soy", "soy"), ("egg", "egg")]:
        if KB.contains_group(text, group):
            personal = (
                (group == "gluten" and (_has_allergy(profile, "gluten") or _has_condition(profile, "celiac")))
                or (group == "dairy" and (_has_allergy(profile, "dairy") or _has_condition(profile, "lactose")))
                or (group == "nuts" and _has_allergy(profile, "nut", "peanut"))
                or (group == "soy" and _has_allergy(profile, "soy"))
                or (group == "egg" and _has_allergy(profile, "egg"))
            )
            if personal:
                concerns.append(f"🚫 **{label}** — flagged for your profile")
    # Nutrient concerns
    if _sugar(product) >= 20:
        concerns.append(f"⚠️ very high **sugar** ({_sugar(product):.0f} g/100 g)")
    if _sodium(product) >= 600:
        concerns.append(f"⚠️ high **sodium** ({_sodium(product):.0f} mg/100 g)")
    # Knowledge-base flagged additives
    for name, entry in KB.find_known_ingredients(text):
        if entry["category"] in ("Preservative", "Colouring") or name in ("palm oil",):
            concerns.append(f"• **{name.title()}** — {entry['health_effects']}")
    if not concerns:
        return f"Good news — I don't see any ingredient in **{_name(product)}** that's a red flag for you."
    return "The ingredients worth watching in **{}**:\n{}".format(_name(product), "\n".join(concerns[:6]))


def _reply_explain_ingredients(profile, product) -> str:
    text = _ingredient_text(product)
    if not text:
        return f"I don't have an ingredient list for **{_name(product)}**."
    found = KB.find_known_ingredients(text)
    if not found:
        return (f"Here's the ingredient list for **{_name(product)}**:\n\n{text}\n\n"
                f"Ask me about any specific ingredient and I'll explain it.")
    lines = [f"• **{name.title()}** ({entry['category']}): {entry['health_effects']}"
             for name, entry in found[:6]]
    return f"Here's what I can tell you about the key ingredients in **{_name(product)}**:\n\n" + "\n".join(lines)


def _reply_what_is_additive(entities) -> str:
    code = entities.get("additive")
    if code:
        info = KB.lookup_additive(code)
        if info:
            return info
        return (f"{code.upper()} is a food additive. I don't have a detailed note for that exact "
                f"code offline, but additives with E-numbers are regulated colours, preservatives, "
                f"emulsifiers or sweeteners.")
    return "Tell me the additive code (for example \"What is E471?\") and I'll explain it."


def _reply_preservatives() -> str:
    entry = KB.INGREDIENT_KB["preservatives"]
    return (f"**Preservatives** ({entry['category']}): {entry['health_effects']}\n\n"
            f"Common ones include sodium benzoate (E211), potassium sorbate (E202), and BHA/BHT. "
            f"They're safe within regulated limits, though it's sensible not to rely on heavily "
            f"preserved foods every day.")


def _reply_condition(profile, product, rating, reasons, condition_key, label,
                     nutrient_hint) -> str:
    has_it = _has_condition(profile, *condition_key) if condition_key else False
    verdict = _verdict_sentence(rating, product)
    intro = (f"Since you're managing **{label}**, " if has_it
             else f"For someone with **{label}**, ")
    return f"{intro}here's my read on **{_name(product)}**:\n\n{verdict}\n\n{nutrient_hint}\n\n{_reasons_block(reasons)}"


def _reply_summarize(profile, product, rating, reasons) -> str:
    sugar, sodium = _sugar(product), _sodium(product)
    bits = []
    if sugar:
        bits.append(f"sugar {sugar:.1f} g/100 g")
    if sodium:
        bits.append(f"sodium {sodium:.0f} mg/100 g")
    nut = (" · ".join(bits)) if bits else "no nutrition data on file"
    brand = product.get("brand")
    header = f"**{_name(product)}**" + (f" by {brand}" if brand else "")
    return (f"{header}\n"
            f"{RATE_EMOJI.get(rating,'')} Rating for you: **{rating.upper()}**\n"
            f"Nutrition: {nut}\n\n"
            f"{_reasons_block(reasons, limit=3)}")


def _reply_recommendation(profile, product, rating, reasons, alternatives) -> str:
    verdict = _verdict_sentence(rating, product)
    if rating == "safe":
        return f"{verdict}\n\nMy recommendation: go ahead and enjoy it in normal portions. 🌿"
    tail = ""
    if alternatives:
        alt = "\n".join(f"• {a}" for a in alternatives)
        tail = f"\n\nYou might prefer these instead:\n{alt}"
    return f"{verdict}\n\n{_reasons_block(reasons)}{tail}"


def _reply_alternatives(profile, product, alternatives) -> str:
    if not product:
        return "Scan a product first and I'll suggest healthier alternatives from our catalogue."
    if not alternatives:
        return (f"I couldn't find a clearly better alternative to **{_name(product)}** in the same "
                f"category right now. Look for options lower in sugar, sodium and additives.")
    alt = "\n".join(f"• {a}" for a in alternatives)
    return (f"Here are healthier options similar to **{_name(product)}** that fit your profile:\n\n{alt}")


# General (no product in context) guidance — preserves the standalone chat's
# usefulness for condition/diet questions asked without a scanned product.
_GENERAL_GUIDANCE = {
    I.GOOD_FOR_DIABETES: (
        "**Managing diabetes:**\n"
        "• 🚫 Limit added sugar, high-fructose corn syrup, dextrose and maltose\n"
        "• ✅ Prefer whole grains, vegetables and lean protein\n"
        "• Aim for under ~5 g sugar per 100 g in packaged foods"),
    I.GOOD_FOR_BP: (
        "**High blood pressure:**\n"
        "• 🚫 Keep sodium low — watch processed foods, canned soups, pickles and sauces\n"
        "• ✅ Choose fresh produce, whole grains and potassium-rich foods\n"
        "• Products over ~600 mg sodium per 100 g are high-sodium"),
    I.GOOD_FOR_HEART: (
        "**Heart health:**\n"
        "• 🚫 Avoid trans fats (partially hydrogenated oils)\n"
        "• ⚠️ Limit saturated fat and processed meats\n"
        "• ✅ Favour olive oil, nuts, fish, whole grains and vegetables"),
    I.GOOD_FOR_KIDNEY: (
        "**Kidney health:**\n"
        "• 🚫 Restrict sodium; watch potassium and phosphorus if advised by your doctor\n"
        "• ⚠️ Go easy on processed and preserved foods\n"
        "• ✅ Portion-control protein as recommended for your stage"),
    I.GOOD_FOR_LACTOSE: (
        "**Lactose intolerance:**\n"
        "• ⚠️ Watch for milk, cream, whey, casein and milk powder\n"
        "• ✅ Hard aged cheeses and lactose-free products are usually well tolerated\n"
        "• Lactase supplements can help with occasional dairy"),
    I.GOOD_FOR_CELIAC: (
        "**Celiac disease:**\n"
        "• 🚫 Strictly avoid wheat, barley, rye, malt, semolina and spelt\n"
        "• ⚠️ Watch hidden gluten in sauces and modified starch\n"
        "• ✅ Safe grains: rice, quinoa, corn and certified gluten-free oats"),
    I.HIGH_SUGAR: (
        "**About sugar:**\n"
        "• The WHO suggests under ~25 g of free sugars per day\n"
        "• Hidden sugars: corn syrup, dextrose, fructose, maltose\n"
        "• Prefer products with under ~5 g sugar per 100 g"),
    I.HIGH_SODIUM: (
        "**About sodium:**\n"
        "• The WHO suggests under ~2000 mg sodium per day\n"
        "• Low-sodium is roughly under 120 mg per 100 g\n"
        "• Most processed and packaged foods are high in sodium"),
    I.IS_VEGAN: (
        "**Vegan tips:** watch for gelatin, carmine (E120), casein/whey, isinglass, "
        "honey and lard. Certified vegan labels give extra assurance."),
    I.IS_VEGETARIAN: (
        "**Vegetarian tips:** watch for gelatin, rennet in some cheeses, and carmine "
        "(E120) used as red colouring."),
}


def _reply_no_product(profile, intent) -> str:
    name = profile.get("name") or "there"
    guidance = _GENERAL_GUIDANCE.get(intent)
    if guidance:
        return (f"{guidance}\n\nScan a product and I'll tell you specifically whether **it** "
                f"fits your profile.")
    return (f"I don't have a product in context yet, {name}. Scan a product (or open the chat from a "
            f"scan result) and I'll answer that about the specific item. In the meantime, I can "
            f"explain ingredients, additives (e.g. \"What is E471?\"), or give general guidance for "
            f"your health conditions.")


def _reply_unknown(profile, product) -> str:
    suggestions = ("• \"Can I eat this?\"\n• \"Is it high in sugar?\"\n"
                   "• \"Does it contain gluten?\"\n• \"Suggest a healthier alternative\"\n"
                   "• \"Explain the ingredients\"")
    where = f" about **{_name(product)}**" if product else ""
    return f"I'm not sure I caught that. Here are some things you can ask me{where}:\n\n{suggestions}"


# ──────────────────────────────────────────────────────────────────────────
# Alternatives ranking
# ──────────────────────────────────────────────────────────────────────────
def _rank_alternatives(product: Optional[dict], profile: dict,
                       candidates: list[dict], rate_fn: Callable,
                       max_items: int = 3) -> list[str]:
    """
    From same-category candidate products, return names of items that are
    rated 'safe' for this user (never recommend a conflicting product).
    """
    if not product or not candidates or rate_fn is None:
        return []
    current_barcode = product.get("barcode")
    picks: list[str] = []
    for cand in candidates:
        if cand.get("barcode") == current_barcode:
            continue
        try:
            rating, _, _, _ = rate_fn(cand, profile)
        except Exception:
            continue
        if rating == "safe":
            label = cand.get("product_name") or "Unknown"
            brand = cand.get("brand")
            picks.append(f"{label}" + (f" ({brand})" if brand else ""))
        if len(picks) >= max_items:
            break
    return picks


# ──────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────
def generate_reply(message: str,
                   profile: dict,
                   product: Optional[dict],
                   rating_result: Optional[tuple],
                   history: list[dict],
                   candidates: Optional[list[dict]] = None,
                   rate_fn: Optional[Callable] = None) -> dict:
    """
    Produce a chatbot reply.

    Returns {"reply": str, "intent": str, "rating": Optional[str]}.
    """
    from .memory import last_bot_context
    last_intent, last_rating = last_bot_context(history)

    intent, entities = I.detect_intent(message, last_intent=last_intent, last_rating=last_rating)

    # Unpack the rule-engine prediction for the active product (if any)
    rating: Optional[str] = None
    reasons: list[str] = []
    if rating_result:
        rating, _conf, _proba, reasons = rating_result

    # Intents that don't need a product
    if intent == I.GREETING:
        return {"reply": _reply_greeting(profile, product), "intent": intent, "rating": rating}
    if intent == I.WHAT_IS_ADDITIVE:
        return {"reply": _reply_what_is_additive(entities), "intent": intent, "rating": rating}
    if intent == I.WHAT_PRESERVATIVES:
        return {"reply": _reply_preservatives(), "intent": intent, "rating": rating}

    # Everything below is best answered with a product in context. When there
    # is none, fall back to general guidance (condition/diet/nutrient intents)
    # or a helpful prompt to scan a product.
    if product is None:
        return {"reply": _reply_no_product(profile, intent), "intent": intent, "rating": None}

    alternatives = _rank_alternatives(product, profile, candidates or [], rate_fn)

    dispatch = {
        I.CAN_I_EAT:    lambda: _reply_can_i_eat(profile, product, rating, reasons),
        I.IS_SAFE:      lambda: _reply_is_safe(profile, product, rating, reasons),
        I.IS_HEALTHY:   lambda: _reply_is_healthy(profile, product, rating, reasons),
        I.WHY:          lambda: _reply_why(profile, product, rating, reasons, positive=(rating == "safe")),
        I.WHY_SAFE:     lambda: _reply_why(profile, product, rating, reasons, positive=True),
        I.WHY_AVOID:    lambda: _reply_why(profile, product, rating, reasons, positive=False),
        I.CONTAINS_GLUTEN: lambda: _reply_contains(profile, product, "gluten", "gluten"),
        I.CONTAINS_DAIRY:  lambda: _reply_contains(profile, product, "dairy", "dairy"),
        I.CONTAINS_NUTS:   lambda: _reply_contains(profile, product, "nuts", "nuts"),
        I.CONTAINS_SOY:    lambda: _reply_contains(profile, product, "soy", "soy"),
        I.CONTAINS_EGG:    lambda: _reply_contains(profile, product, "egg", "egg"),
        I.IS_VEGAN:        lambda: _reply_is_vegan(profile, product),
        I.IS_VEGETARIAN:   lambda: _reply_is_vegetarian(profile, product),
        I.HIGH_SUGAR:      lambda: _reply_high_sugar(profile, product),
        I.HIGH_SODIUM:     lambda: _reply_high_sodium(profile, product),
        I.DANGEROUS_INGREDIENT: lambda: _reply_dangerous_ingredient(profile, product),
        I.EXPLAIN_INGREDIENTS:  lambda: _reply_explain_ingredients(profile, product),
        I.SUMMARIZE:    lambda: _reply_summarize(profile, product, rating, reasons),
        I.RECOMMENDATION: lambda: _reply_recommendation(profile, product, rating, reasons, alternatives),
        I.ALTERNATIVES: lambda: _reply_alternatives(profile, product, alternatives),
        I.GOOD_FOR_DIABETES: lambda: _reply_condition(
            profile, product, rating, reasons, ("diabetes",), "diabetes",
            _reply_high_sugar(profile, product)),
        I.GOOD_FOR_BP: lambda: _reply_condition(
            profile, product, rating, reasons, ("bp", "blood pressure", "hypertension"),
            "high blood pressure", _reply_high_sodium(profile, product)),
        I.GOOD_FOR_HEART: lambda: _reply_condition(
            profile, product, rating, reasons, ("heart",), "heart disease",
            "Watch saturated fat, trans fat and sodium in particular."),
        I.GOOD_FOR_KIDNEY: lambda: _reply_condition(
            profile, product, rating, reasons, ("kidney",), "kidney disease",
            _reply_high_sodium(profile, product)),
        I.GOOD_FOR_LACTOSE: lambda: _reply_condition(
            profile, product, rating, reasons, ("lactose",), "lactose intolerance",
            _reply_contains(profile, product, "dairy", "dairy")),
        I.GOOD_FOR_CELIAC: lambda: _reply_condition(
            profile, product, rating, reasons, ("celiac",), "celiac disease",
            _reply_contains(profile, product, "gluten", "gluten")),
    }

    handler = dispatch.get(intent)
    reply = handler() if handler else _reply_unknown(profile, product)
    return {"reply": reply, "intent": intent, "rating": rating}
