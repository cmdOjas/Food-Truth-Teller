"""Tests for the NLP preprocessing pipeline."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ml"))

from nlp_processor import NLPProcessor


def test_lowercase():
    p = NLPProcessor()
    result = p.process("SUGAR Glucose Fructose")
    assert result == result.lower()


def test_removes_punctuation():
    p = NLPProcessor()
    result = p.process("sugar, salt, (water)")
    assert "," not in result
    assert "(" not in result


def test_additive_normalization():
    p = NLPProcessor()
    result = p.process("monosodium glutamate and high fructose corn syrup")
    assert "msg" in result
    assert "hfcs" in result


def test_empty_input():
    p = NLPProcessor()
    assert p.process("") == ""


def test_extract_features_has_hfcs():
    p = NLPProcessor()
    features = p.extract_features("high fructose corn syrup, sugar, water")
    assert features["has_hfcs"] == 1


def test_extract_features_clean():
    p = NLPProcessor()
    features = p.extract_features("organic apples, water, lemon juice")
    assert features["has_hfcs"] == 0
    assert features["has_trans_fat"] == 0
    assert features["has_msg"] == 0


def test_hydrogenated_detected():
    p = NLPProcessor()
    features = p.extract_features("partially hydrogenated soybean oil, sugar")
    assert features["has_trans_fat"] == 1


def test_ingredient_count():
    p = NLPProcessor()
    features = p.extract_features("sugar water salt")
    assert features["ingredient_count"] > 0
