"""Barcode scan endpoint."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, ValidationError
from app.services.openfoodfacts import OpenFoodFactsService
from app.models.product import Product

scan_bp = Blueprint("scan", __name__)
off_service = OpenFoodFactsService()


class ScanSchema(Schema):
    barcode = fields.Str(required=True)


@scan_bp.post("/scan")
@jwt_required()
def scan():
    """
    Accept a barcode and return the product data.
    Fetches from Open Food Facts if not cached locally.
    """
    schema = ScanSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 422

    barcode = data["barcode"].strip()
    product = Product.query.filter_by(barcode=barcode).first()
    if product:
        return jsonify({"product": product.to_dict(), "source": "local"}), 200

    product = off_service.fetch_and_store(barcode)
    if not product:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404

    return jsonify({"product": product.to_dict(), "source": "openfoodfacts"}), 200
