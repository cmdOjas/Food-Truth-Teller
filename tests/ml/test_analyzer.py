"""Tests for the IngredientAnalyzer service."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

import pytest


class MockProfile:
    health_conditions = ["Diabetes", "Celiac Disease"]
    allergies = ["gluten"]
    diet_preference = "vegetarian"


class MockProduct:
    ingredients_text = "sugar, hydrogenated oil, gluten, red 40, sodium benzoate"
    nutrition_per_100g = {"sugars_g": 35, "sodium_mg": 800, "saturated_fat_g": 6}
    allergens = []
    additives = []
    nutriscore_grade = "e"
    nova_group = 4
    is_vegetarian = True
    is_vegan = False


class MockSafeProduct:
    ingredients_text = "water, brown rice, olive oil, sea salt"
    nutrition_per_100g = {"sugars_g": 1, "sodium_mg": 50, "saturated_fat_g": 0.5}
    allergens = []
    additives = []
    nutriscore_grade = "a"
    nova_group = 1
    is_vegetarian = True
    is_vegan = True


def test_analyzer_flags_high_risk(app):
    """Dangerous product with matching user conditions should flag Avoid."""
    from app.services.analyzer import IngredientAnalyzer
    analyzer = IngredientAnalyzer()
    result = analyzer.analyze(MockProduct(), MockProfile())
    assert result["prediction"] in ("Avoid", "Caution")
    assert len(result["all_flags"]) > 0


def test_analyzer_safe_product(app):
    """Clean product with safe user profile should not trigger high-risk."""
    from app.services.analyzer import IngredientAnalyzer

    class SafeProfile:
        health_conditions = []
        allergies = []
        diet_preference = "none"

    analyzer = IngredientAnalyzer()
    result = analyzer.analyze(MockSafeProduct(), SafeProfile())
    high_issues = [i for i in result["all_flags"] if i["severity"] == "high"]
    assert len(high_issues) == 0


def test_analyzer_returns_confidence(app):
    from app.services.analyzer import IngredientAnalyzer
    analyzer = IngredientAnalyzer()
    result = analyzer.analyze(MockProduct(), MockProfile())
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 100


def test_analyzer_no_profile(app):
    """Analyzer should work even if profile is None."""
    from app.services.analyzer import IngredientAnalyzer
    analyzer = IngredientAnalyzer()
    result = analyzer.analyze(MockSafeProduct(), None)
    assert "prediction" in result
