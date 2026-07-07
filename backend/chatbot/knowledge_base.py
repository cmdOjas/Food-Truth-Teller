"""
Ingredient Knowledge Base for the offline nutrition chatbot.

This module is fully self-contained and offline. It holds:

  1. INGREDIENT_KB  — structured facts for common food ingredients / additives
  2. ADDITIVE_INFO  — plain-language meaning of E-number additives
  3. ALLERGEN_GROUPS — keyword groups used to detect an allergen inside a
                       product's free-text ingredient list
  4. helper functions to scan a product's ingredient text

Each INGREDIENT_KB entry uses a consistent schema so it can be extended
without touching the engine:

    {
        "category":        str,          # e.g. "Sweetener", "Preservative"
        "health_effects":  str,          # short human-friendly summary
        "allergy":         str,          # allergy note ("None known" if safe)
        "vegan":           bool | None,  # None = depends on source
        "vegetarian":      bool | None,
        "diabetes":        str,          # impact for diabetics
        "blood_pressure":  str,
        "kidney":          str,
        "heart":           str,
        "lactose":         str,
        "gluten":          str,
    }

The structure is intentionally plain Python dicts so it can be serialised
to JSON, stored in a DB, or edited by non-engineers.
"""
from __future__ import annotations

import re
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────
# 1. Ingredient knowledge base
# ──────────────────────────────────────────────────────────────────────────
INGREDIENT_KB: dict[str, dict] = {
    "sugar": {
        "category": "Sweetener",
        "health_effects": "Adds empty calories and spikes blood glucose. Excess intake is linked to weight gain, tooth decay and type-2 diabetes.",
        "allergy": "None known",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "High impact — raises blood sugar quickly. Diabetics should strictly limit it.",
        "blood_pressure": "Indirect risk — excess sugar promotes weight gain which raises blood pressure.",
        "kidney": "Neutral in small amounts, but poor glucose control harms kidneys over time.",
        "heart": "High added sugar is associated with higher triglycerides and heart disease risk.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "salt": {
        "category": "Seasoning / Sodium source",
        "health_effects": "Provides sodium needed by the body, but excess raises blood pressure and fluid retention.",
        "allergy": "None known",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral for blood sugar.",
        "blood_pressure": "High impact — the main dietary driver of high blood pressure.",
        "kidney": "High impact — kidney patients must restrict sodium to control fluid and pressure.",
        "heart": "Excess sodium strains the heart and arteries.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "palm oil": {
        "category": "Fat / Oil",
        "health_effects": "High in saturated fat. Cheap and common in processed foods; excess raises LDL cholesterol.",
        "allergy": "None known",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral for glucose, but calorie-dense.",
        "blood_pressure": "Neutral directly.",
        "kidney": "Neutral.",
        "heart": "Higher risk — saturated fat can raise LDL ('bad') cholesterol.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "msg": {
        "category": "Flavour enhancer",
        "health_effects": "Monosodium glutamate boosts savoury flavour. Generally recognised as safe; some people report sensitivity (headache, flushing).",
        "allergy": "May trigger sensitivity in some individuals",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral for blood sugar.",
        "blood_pressure": "Contains sodium — contributes to total sodium intake.",
        "kidney": "Adds sodium; moderate for kidney patients.",
        "heart": "Neutral in normal amounts.",
        "lactose": "Lactose-free.",
        "gluten": "Usually gluten-free.",
    },
    "citric acid": {
        "category": "Acidity regulator / Preservative",
        "health_effects": "A mild acid used for tartness and preservation. Safe for almost everyone in food amounts.",
        "allergy": "None known",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral.",
        "blood_pressure": "Neutral.",
        "kidney": "Neutral; can even help reduce certain kidney stones.",
        "heart": "Neutral.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "e471": {
        "category": "Emulsifier (mono- and diglycerides of fatty acids)",
        "health_effects": "Keeps fats and water mixed in baked goods and spreads. Safe in normal amounts.",
        "allergy": "None known",
        "vegan": None,  # can be plant- or animal-derived
        "vegetarian": None,
        "diabetes": "Neutral.",
        "blood_pressure": "Neutral.",
        "kidney": "Neutral.",
        "heart": "Neutral, though usually found in processed high-fat foods.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "e500": {
        "category": "Raising agent (sodium bicarbonate / carbonate)",
        "health_effects": "Baking soda used to make baked goods rise. Safe in food amounts.",
        "allergy": "None known",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral.",
        "blood_pressure": "Contains sodium — minor contribution.",
        "kidney": "Adds a little sodium.",
        "heart": "Neutral.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "carrageenan": {
        "category": "Thickener / Stabiliser (from seaweed)",
        "health_effects": "Gives creamy texture to dairy and plant milks. Some people report digestive discomfort.",
        "allergy": "May cause digestive sensitivity in some people",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral.",
        "blood_pressure": "Neutral.",
        "kidney": "Neutral.",
        "heart": "Neutral.",
        "lactose": "Lactose-free (even though often used in dairy).",
        "gluten": "Gluten-free.",
    },
    "milk powder": {
        "category": "Dairy",
        "health_effects": "Dried milk used in chocolate, baked goods and beverages. A source of protein and calcium.",
        "allergy": "Milk allergen",
        "vegan": False,
        "vegetarian": True,
        "diabetes": "Contains natural lactose sugar — moderate.",
        "blood_pressure": "Neutral.",
        "kidney": "Contains phosphorus and potassium — moderate for kidney patients.",
        "heart": "Whole-milk powder adds saturated fat.",
        "lactose": "Contains lactose — unsuitable for lactose intolerance.",
        "gluten": "Gluten-free.",
    },
    "casein": {
        "category": "Dairy protein",
        "health_effects": "The main protein in milk, used in cheese and protein products.",
        "allergy": "Milk allergen",
        "vegan": False,
        "vegetarian": True,
        "diabetes": "Neutral for blood sugar.",
        "blood_pressure": "Neutral.",
        "kidney": "High-protein; moderate for advanced kidney disease.",
        "heart": "Neutral.",
        "lactose": "Milk-derived; usually very low lactose but still a dairy protein.",
        "gluten": "Gluten-free.",
    },
    "wheat flour": {
        "category": "Grain / Flour",
        "health_effects": "Ground wheat used in bread, pasta and baked goods. Contains gluten.",
        "allergy": "Wheat allergen",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Refined wheat flour is high-GI and raises blood sugar; prefer whole grain.",
        "blood_pressure": "Neutral.",
        "kidney": "Neutral.",
        "heart": "Refined flour is less heart-friendly than whole grain.",
        "lactose": "Lactose-free.",
        "gluten": "Contains gluten — unsafe for celiac disease.",
    },
    "barley": {
        "category": "Grain",
        "health_effects": "A fibre-rich grain, but it contains gluten.",
        "allergy": "Gluten-related",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Whole barley is high-fibre and lower-GI — reasonable in moderation.",
        "blood_pressure": "Neutral to helpful (fibre).",
        "kidney": "Neutral.",
        "heart": "Beta-glucan fibre can help lower cholesterol.",
        "lactose": "Lactose-free.",
        "gluten": "Contains gluten — unsafe for celiac disease.",
    },
    "oats": {
        "category": "Grain",
        "health_effects": "Whole-grain, high in soluble fibre (beta-glucan). Heart-friendly.",
        "allergy": "Usually safe; risk of gluten cross-contamination",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Low-GI, high fibre — good choice in moderation.",
        "blood_pressure": "Helpful — fibre supports healthy blood pressure.",
        "kidney": "Neutral.",
        "heart": "Beneficial — soluble fibre lowers cholesterol.",
        "lactose": "Lactose-free.",
        "gluten": "Naturally gluten-free, but only certified oats are safe for celiacs.",
    },
    "soy lecithin": {
        "category": "Emulsifier (from soy)",
        "health_effects": "Keeps ingredients blended, common in chocolate. Present in tiny amounts.",
        "allergy": "Soy-derived (very low residual soy protein)",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral.",
        "blood_pressure": "Neutral.",
        "kidney": "Neutral.",
        "heart": "Neutral.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "peanuts": {
        "category": "Legume / Nut",
        "health_effects": "Protein- and fat-rich legume. A very common and potentially severe allergen.",
        "allergy": "Peanut allergen — can cause anaphylaxis",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Low-GI, generally good in moderation.",
        "blood_pressure": "Choose unsalted — salted versions add sodium.",
        "kidney": "High in potassium and phosphorus — moderate for kidney patients.",
        "heart": "Unsalted peanuts contain heart-healthy fats.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "tree nuts": {
        "category": "Nut",
        "health_effects": "Almonds, cashews, walnuts etc. Nutritious but a common allergen.",
        "allergy": "Tree-nut allergen — can cause anaphylaxis",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Low-GI, good in moderation.",
        "blood_pressure": "Choose unsalted.",
        "kidney": "High potassium/phosphorus — moderate for kidney patients.",
        "heart": "Heart-healthy unsaturated fats.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "egg powder": {
        "category": "Egg product",
        "health_effects": "Dried egg used in baked goods and mayonnaise. Good protein source.",
        "allergy": "Egg allergen",
        "vegan": False,
        "vegetarian": True,
        "diabetes": "Neutral for blood sugar.",
        "blood_pressure": "Neutral.",
        "kidney": "High-quality protein; moderate for advanced kidney disease.",
        "heart": "Neutral for most people in moderation.",
        "lactose": "Lactose-free.",
        "gluten": "Gluten-free.",
    },
    "artificial colors": {
        "category": "Colouring",
        "health_effects": "Synthetic dyes (e.g. Red 40, Yellow 5). Some are linked to hyperactivity in sensitive children.",
        "allergy": "May trigger sensitivity in some individuals",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral.",
        "blood_pressure": "Neutral.",
        "kidney": "Neutral.",
        "heart": "Neutral.",
        "lactose": "Lactose-free.",
        "gluten": "Usually gluten-free.",
    },
    "preservatives": {
        "category": "Preservative",
        "health_effects": "Extend shelf life (e.g. BHA, BHT, sodium benzoate). Safe within limits; some are debated for long-term use.",
        "allergy": "Certain preservatives may trigger sensitivity",
        "vegan": True,
        "vegetarian": True,
        "diabetes": "Neutral.",
        "blood_pressure": "Sodium-based preservatives add a little sodium.",
        "kidney": "Sodium-based ones add sodium.",
        "heart": "Neutral in normal amounts.",
        "lactose": "Lactose-free.",
        "gluten": "Usually gluten-free.",
    },
}

# ──────────────────────────────────────────────────────────────────────────
# 2. E-number additive dictionary (plain-language meanings)
# ──────────────────────────────────────────────────────────────────────────
ADDITIVE_INFO: dict[str, str] = {
    "e100": "E100 (Curcumin) — a natural yellow colour from turmeric.",
    "e102": "E102 (Tartrazine) — a synthetic yellow dye; can cause sensitivity in some people.",
    "e110": "E110 (Sunset Yellow) — a synthetic orange-yellow dye.",
    "e120": "E120 (Carmine) — a red colour made from insects; not vegan or vegetarian.",
    "e129": "E129 (Allura Red) — a synthetic red dye.",
    "e150": "E150 (Caramel colour) — a common brown colour in colas and sauces.",
    "e202": "E202 (Potassium sorbate) — a widely used, safe preservative.",
    "e211": "E211 (Sodium benzoate) — a preservative; adds a little sodium.",
    "e250": "E250 (Sodium nitrite) — a preservative/colour fixer used in cured meats.",
    "e300": "E300 (Ascorbic acid / Vitamin C) — an antioxidant preservative.",
    "e322": "E322 (Lecithin) — an emulsifier, often from soy or sunflower.",
    "e330": "E330 (Citric acid) — a common, safe acidity regulator.",
    "e407": "E407 (Carrageenan) — a seaweed-derived thickener.",
    "e471": "E471 (Mono- and diglycerides of fatty acids) — an emulsifier; may be plant- or animal-derived.",
    "e500": "E500 (Sodium bicarbonate) — baking soda, a raising agent.",
    "e621": "E621 (Monosodium glutamate / MSG) — a flavour enhancer that adds sodium.",
    "e951": "E951 (Aspartame) — an artificial sweetener; unsafe for people with PKU.",
    "e955": "E955 (Sucralose) — a no-calorie artificial sweetener.",
}

# ──────────────────────────────────────────────────────────────────────────
# 3. Allergen / group keyword sets — used to detect an allergen inside a
#    product's free-text ingredient list. Self-contained (no import from app).
# ──────────────────────────────────────────────────────────────────────────
ALLERGEN_GROUPS: dict[str, list[str]] = {
    "gluten": ["wheat", "barley", "rye", "gluten", "semolina", "spelt", "kamut", "malt"],
    "dairy":  ["milk", "cream", "cheese", "butter", "whey", "casein", "lactose",
               "skim milk", "milk powder", "ghee", "paneer"],
    "nuts":   ["peanut", "almond", "cashew", "walnut", "hazelnut", "pecan",
               "pistachio", "macadamia", "tree nut"],
    "soy":    ["soy", "soya", "soybean", "soy lecithin"],
    "egg":    ["egg", "albumin", "ovalbumin", "egg powder"],
}

# Non-vegetarian / non-vegan marker ingredients (for veg/vegan questions)
NON_VEGETARIAN_MARKERS: list[str] = [
    "chicken", "beef", "pork", "mutton", "lamb", "turkey", "fish", "salmon",
    "tuna", "shrimp", "prawn", "anchovy", "sardine", "crab", "lobster",
    "gelatin", "lard", "tallow", "suet", "rennet", "carmine", "isinglass",
    "bone broth", "meat extract", "poultry",
]
NON_VEGAN_MARKERS: list[str] = NON_VEGETARIAN_MARKERS + [
    "milk", "cream", "cheese", "butter", "whey", "casein", "lactose", "ghee",
    "paneer", "milk powder", "honey", "egg", "albumin",
]

_E_NUMBER_RE = re.compile(r"\be\s?-?\s?(\d{3,4})\b", re.IGNORECASE)


# ──────────────────────────────────────────────────────────────────────────
# 4. Helper functions
# ──────────────────────────────────────────────────────────────────────────
def _norm(text: Optional[str]) -> str:
    return (text or "").lower()


def contains_group(ingredient_text: Optional[str], group: str) -> bool:
    """Return True if any keyword for *group* appears in the ingredient text."""
    text = _norm(ingredient_text)
    return any(kw in text for kw in ALLERGEN_GROUPS.get(group, []))


def is_probably_vegan(ingredient_text: Optional[str]) -> bool:
    text = _norm(ingredient_text)
    return not any(m in text for m in NON_VEGAN_MARKERS)


def is_probably_vegetarian(ingredient_text: Optional[str]) -> bool:
    text = _norm(ingredient_text)
    return not any(m in text for m in NON_VEGETARIAN_MARKERS)


def find_known_ingredients(ingredient_text: Optional[str]) -> list[tuple[str, dict]]:
    """
    Return a list of (name, kb_entry) for every knowledge-base ingredient
    whose name appears in the product's ingredient text.
    """
    text = _norm(ingredient_text)
    found: list[tuple[str, dict]] = []
    for name, entry in INGREDIENT_KB.items():
        # skip pure E-number keys here; those are matched separately
        if name.startswith("e") and name[1:].isdigit():
            if name in text.replace(" ", "").replace("-", ""):
                found.append((name, entry))
        elif name in text:
            found.append((name, entry))
    return found


def find_additive_codes(text: Optional[str]) -> list[str]:
    """Extract E-number codes (e.g. 'e471') mentioned in *text*."""
    codes = []
    for m in _E_NUMBER_RE.finditer(_norm(text)):
        codes.append("e" + m.group(1))
    return codes


def lookup_ingredient(name: str) -> Optional[dict]:
    """Look up a single ingredient by (fuzzy) name."""
    key = _norm(name).strip()
    if key in INGREDIENT_KB:
        return INGREDIENT_KB[key]
    # try a loose contains match
    for kb_name, entry in INGREDIENT_KB.items():
        if kb_name in key or key in kb_name:
            return entry
    return None


def lookup_additive(code: str) -> Optional[str]:
    """Look up an E-number additive description."""
    return ADDITIVE_INFO.get(_norm(code).replace(" ", "").replace("-", ""))
