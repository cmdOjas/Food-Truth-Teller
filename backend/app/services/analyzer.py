"""
Ingredient analyzer: maps raw ingredients to health risk signals,
then optionally runs the ML model for a prediction score.
"""
from __future__ import annotations
import os
import re
import joblib
from typing import Optional
from flask import current_app

HARMFUL_PATTERNS: dict[str, dict] = {
    "high_sugar": {
        "keywords": ["sugar", "sucrose", "glucose", "fructose", "corn syrup", "high fructose corn syrup", "cane sugar", "dextrose", "maltose"],
        "risk_for": ["diabetes", "obesity", "dental caries"],
    },
    "artificial_sweeteners": {
        "keywords": ["aspartame", "sucralose", "saccharin", "acesulfame", "stevia", "sorbitol", "xylitol", "erythritol"],
        "risk_for": ["ibs", "gut sensitivity"],
    },
    "preservatives": {
        "keywords": ["sodium benzoate", "potassium sorbate", "bha", "bht", "tbhq", "nitrate", "nitrite", "e211", "e212", "e320", "e321"],
        "risk_for": ["allergy", "hyperactivity"],
    },
    "artificial_colors": {
        "keywords": ["tartrazine", "sunset yellow", "carmoisine", "brilliant blue", "e102", "e110", "e122", "e129", "e133", "red 40", "yellow 5"],
        "risk_for": ["hyperactivity", "allergy"],
    },
    "msg": {
        "keywords": ["monosodium glutamate", "msg", "e621", "glutamate"],
        "risk_for": ["headache", "sensitivity"],
    },
    "gluten": {
        "keywords": ["wheat", "barley", "rye", "oats", "spelt", "kamut", "semolina", "gluten"],
        "risk_for": ["celiac disease", "gluten intolerance", "gluten sensitivity"],
    },
    "dairy": {
        "keywords": ["milk", "lactose", "whey", "casein", "butter", "cream", "cheese", "yogurt"],
        "risk_for": ["lactose intolerance", "dairy allergy", "milk allergy"],
    },
    "soy": {
        "keywords": ["soy", "soya", "soybean", "tofu", "tempeh", "edamame"],
        "risk_for": ["soy allergy"],
    },
    "eggs": {
        "keywords": ["egg", "albumin", "ovalbumin", "mayonnaise"],
        "risk_for": ["egg allergy"],
    },
    "nuts": {
        "keywords": ["peanut", "almond", "cashew", "walnut", "hazelnut", "pecan", "pistachio", "macadamia", "tree nut"],
        "risk_for": ["nut allergy", "peanut allergy"],
    },
    "palm_oil": {
        "keywords": ["palm oil", "palm fat", "palm kernel"],
        "risk_for": ["cardiovascular disease", "high cholesterol"],
    },
    "trans_fat": {
        "keywords": ["hydrogenated", "partially hydrogenated", "trans fat", "shortening"],
        "risk_for": ["cardiovascular disease", "high cholesterol"],
    },
    "high_sodium": {
        "keywords": ["sodium", "salt", "monosodium"],
        "risk_for": ["hypertension", "kidney disease", "heart disease"],
    },
    "saturated_fat": {
        "keywords": ["saturated fat", "lard", "tallow", "coconut oil"],
        "risk_for": ["cardiovascular disease", "high cholesterol"],
    },
    "alcohol": {
        "keywords": ["alcohol", "ethanol", "wine", "beer", "spirits"],
        "risk_for": ["liver disease", "alcohol sensitivity", "pregnancy"],
    },
    "caffeine": {
        "keywords": ["caffeine", "coffee", "guarana", "tea extract", "matcha"],
        "risk_for": ["anxiety", "hypertension", "pregnancy", "insomnia"],
    },
    "animal_ingredients": {
        "keywords": ["gelatin", "lard", "tallow", "rennet", "carmine", "isinglass", "bone char"],
        "risk_for": ["vegan", "vegetarian", "halal", "kosher"],
    },
}

DIET_UNSAFE_CATEGORIES: dict[str, list[str]] = {
    "vegan": ["dairy", "eggs", "animal_ingredients"],
    "vegetarian": ["animal_ingredients"],
    "gluten-free": ["gluten"],
    "keto": ["high_sugar"],
}


class IngredientAnalyzer:
    """Analyzes ingredients against user profile and ML model."""

    def __init__(self) -> None:
        self._model = None
        self._vectorizer = None

    def _load_model(self):
        if self._model is None:
            path = current_app.config.get("ML_MODEL_PATH", "")
            vec_path = current_app.config.get("ML_VECTORIZER_PATH", "")
            if os.path.exists(path) and os.path.exists(vec_path):
                self._model = joblib.load(path)
                self._vectorizer = joblib.load(vec_path)
        return self._model, self._vectorizer

    def analyze(self, product, profile) -> dict:
        ingredients_text = (product.ingredients_text or "").lower()
        issues = []
        detected_categories: set[str] = set()

        user_conditions = [c.lower() for c in (profile.health_conditions if profile else [])]
        user_allergies = [a.lower() for a in (profile.allergies if profile else [])]
        diet = (profile.diet_preference or "none").lower() if profile else "none"

        for category, meta in HARMFUL_PATTERNS.items():
            matched_keywords = [kw for kw in meta["keywords"] if kw in ingredients_text]
            if matched_keywords:
                detected_categories.add(category)
                # Check if this category is risky for the user
                risk_reasons = []
                for risk in meta["risk_for"]:
                    if any(risk in cond for cond in user_conditions) or any(risk in allergy for allergy in user_allergies):
                        risk_reasons.append(risk)

                if diet in DIET_UNSAFE_CATEGORIES and category in DIET_UNSAFE_CATEGORIES[diet]:
                    risk_reasons.append(f"incompatible with {diet} diet")

                issues.append({
                    "category": category,
                    "detected_ingredients": matched_keywords,
                    "risk_reasons": risk_reasons,
                    "severity": "high" if risk_reasons else "low",
                })

        # Nutrition-based checks
        nutrition = product.nutrition_per_100g or {}
        if (nutrition.get("sugars_g") or 0) > 20:
            issues.append({
                "category": "high_sugar_nutrition",
                "detected_ingredients": [f"Sugar: {nutrition['sugars_g']}g/100g"],
                "risk_reasons": ["diabetes"] if "diabetes" in user_conditions else [],
                "severity": "high" if "diabetes" in user_conditions else "medium",
            })
        if (nutrition.get("sodium_mg") or 0) > 600:
            issues.append({
                "category": "high_sodium_nutrition",
                "detected_ingredients": [f"Sodium: {nutrition['sodium_mg']}mg/100g"],
                "risk_reasons": ["hypertension"] if "hypertension" in user_conditions else [],
                "severity": "high" if "hypertension" in user_conditions else "medium",
            })
        if (nutrition.get("saturated_fat_g") or 0) > 5:
            issues.append({
                "category": "high_saturated_fat_nutrition",
                "detected_ingredients": [f"Saturated fat: {nutrition['saturated_fat_g']}g/100g"],
                "risk_reasons": ["cardiovascular disease"] if "cardiovascular disease" in user_conditions else [],
                "severity": "high" if "cardiovascular disease" in user_conditions else "medium",
            })

        high_risk = any(i["severity"] == "high" for i in issues)
        medium_risk = any(i["severity"] == "medium" for i in issues)

        if high_risk:
            prediction = "Avoid"
            base_confidence = 90
        elif medium_risk:
            prediction = "Caution"
            base_confidence = 70
        else:
            prediction = "Safe"
            base_confidence = 85

        # Try ML model for confidence refinement
        model, vectorizer = self._load_model()
        ml_confidence = None
        if model and vectorizer:
            try:
                vec = vectorizer.transform([ingredients_text])
                proba = model.predict_proba(vec)[0]
                ml_class = model.predict(vec)[0]
                ml_confidence = round(max(proba) * 100, 1)
                if ml_class == 1:
                    prediction = "Avoid" if high_risk else "Caution"
                else:
                    if not high_risk and not medium_risk:
                        prediction = "Safe"
                base_confidence = ml_confidence
            except Exception:
                pass

        high_risk_issues = [
            {"ingredient": ", ".join(i["detected_ingredients"][:2]), "reason": f"Contains {i['category'].replace('_', ' ')}: risky for {', '.join(i['risk_reasons']) or 'general health'}"}
            for i in issues if i["severity"] == "high"
        ]

        return {
            "prediction": prediction,
            "confidence": base_confidence,
            "issues": high_risk_issues,
            "all_flags": issues,
            "nutriscore": product.nutriscore_grade,
            "nova_group": product.nova_group,
            "is_vegetarian": product.is_vegetarian,
            "is_vegan": product.is_vegan,
        }
