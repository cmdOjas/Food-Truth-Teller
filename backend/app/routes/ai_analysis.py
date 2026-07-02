"""
AI nutrition analysis route  —  POST /api/ai/analyze

Accepts a barcode (or inline product data) and returns a structured
Phi-3 / RAG-powered nutritional analysis tailored to the authenticated
user's health profile.

Endpoint: POST /api/ai/analyze
Auth:      JWT required
Body:      { "barcode": "049000006346" }
           OR
           { "product": { <inline product dict> } }
Response:  Standard AI analysis JSON object
"""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.product import Product
from app.models.profile import UserProfile
from app.services.openfoodfacts import OpenFoodFactsService

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai_analysis", __name__)
_off  = OpenFoodFactsService()


@ai_bp.post("/ai/analyze")
@jwt_required()
def ai_analyze():
    """
    Full AI nutrition analysis using Phi-3 + RAG.

    Returns the standard analysis schema:
    {
        overall_score, health_rating, summary, pros, cons,
        warnings, recommended_for, avoid_if, better_alternatives,
        daily_limit, personalized_advice, confidence
    }
    """
    body    = request.get_json(force=True) or {}
    barcode = (body.get("barcode") or "").strip()
    inline  = body.get("product")          # optional inline product dict

    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    # ── Resolve product ───────────────────────────────────────────────────────
    if inline:
        product = _dict_to_product(inline)
    elif barcode:
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            product = _off.fetch_and_store(barcode)
        if not product:
            return jsonify({"error": f"Product not found for barcode: {barcode}"}), 404
    else:
        return jsonify({"error": "Provide 'barcode' or 'product' in request body."}), 400

    # ── Run AI analysis ───────────────────────────────────────────────────────
    try:
        from app.ai.parser import analyze_product
        result = analyze_product(product, profile)
    except Exception as exc:
        logger.exception("AI analysis failed: %s", exc)
        return jsonify({"error": "AI analysis failed.", "detail": str(exc)}), 500

    return jsonify(result), 200


@ai_bp.get("/ai/health")
def ai_health():
    """Check if Ollama is reachable and the RAG index is built."""
    from app.ai.ollama_client import is_ollama_running
    from app.ai.rag import retriever
    from app.ai.cache import stats

    ollama_ok = is_ollama_running()
    index_ok  = retriever._built

    return jsonify({
        "ollama_running":  ollama_ok,
        "rag_index_built": index_ok,
        "cache_stats":     stats(),
        "status":          "ok" if ollama_ok else "degraded",
    }), 200 if ollama_ok else 503


@ai_bp.post("/ai/invalidate-cache")
@jwt_required()
def invalidate_cache():
    """Invalidate all cached analyses for the current user (call after profile update)."""
    user_id = int(get_jwt_identity())
    from app.ai.cache import invalidate_user
    removed = invalidate_user(user_id)
    return jsonify({"message": f"Invalidated {removed} cache entries."}), 200


# ── Helpers ───────────────────────────────────────────────────────────────────

class _InlineProduct:
    """Duck-typed product object built from a request dict."""
    def __init__(self, d: dict):
        self.barcode          = d.get("barcode", "")
        self.name             = d.get("name") or d.get("product_name") or "Unknown"
        self.brand            = d.get("brand")
        self.category         = d.get("category")
        self.ingredients_text = d.get("ingredients_text") or d.get("ingredients")
        self.nutrition_per_100g = d.get("nutrition_per_100g") or {}
        self.is_vegetarian    = bool(d.get("is_vegetarian"))
        self.is_vegan         = bool(d.get("is_vegan"))
        self.nutriscore_grade = d.get("nutriscore_grade")
        self.nova_group       = d.get("nova_group")
        self.allergens        = d.get("allergens") or []
        self.additives        = d.get("additives") or []


def _dict_to_product(d: dict) -> _InlineProduct:
    return _InlineProduct(d)
