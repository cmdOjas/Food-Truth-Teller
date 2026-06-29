"""Product lookup and recommendations routes."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.product import Product
from app.services.openfoodfacts import OpenFoodFactsService
from app.services.analyzer import IngredientAnalyzer

product_bp = Blueprint("product", __name__)
off_service = OpenFoodFactsService()
analyzer = IngredientAnalyzer()


@product_bp.get("/product/<string:barcode>")
@jwt_required()
def get_product(barcode: str):
    """Look up a product by barcode. Falls back to Open Food Facts if not in local DB."""
    product = Product.query.filter_by(barcode=barcode).first()
    if not product:
        product = off_service.fetch_and_store(barcode)
        if not product:
            return jsonify({"error": "Product not found"}), 404

    return jsonify(product.to_dict()), 200


@product_bp.get("/recommendations")
@jwt_required()
def get_recommendations():
    """Return healthier product alternatives based on nutriscore."""
    category = request.args.get("category")
    query = Product.query.filter(Product.nutriscore_grade.in_(["a", "b"]))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    products = query.limit(10).all()
    return jsonify([p.to_dict() for p in products]), 200


@product_bp.post("/analyze")
@jwt_required()
def analyze_product():
    """
    Analyze a product's ingredients against the user's health profile using the ML model.
    Body: { barcode: str }
    """
    body = request.get_json(force=True) or {}
    barcode = body.get("barcode")
    if not barcode:
        return jsonify({"error": "barcode is required"}), 400

    product = Product.query.filter_by(barcode=barcode).first()
    if not product:
        product = off_service.fetch_and_store(barcode)
        if not product:
            return jsonify({"error": "Product not found"}), 404

    user_id = int(get_jwt_identity())
    from app.models.profile import UserProfile
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    result = analyzer.analyze(product, profile)
    return jsonify(result), 200
