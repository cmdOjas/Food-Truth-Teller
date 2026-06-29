"""User health profile routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from app import db
from app.models.user import User
from app.models.profile import UserProfile

profile_bp = Blueprint("profile", __name__)


class ProfileSchema(Schema):
    age = fields.Int(validate=validate.Range(min=1, max=150))
    gender = fields.Str(validate=validate.OneOf(["male", "female", "other"]))
    weight_kg = fields.Float(validate=validate.Range(min=1, max=500))
    height_cm = fields.Float(validate=validate.Range(min=30, max=300))
    health_conditions = fields.List(fields.Str())
    allergies = fields.List(fields.Str())
    diet_preference = fields.Str(
        validate=validate.OneOf(
            ["none", "vegetarian", "vegan", "keto", "paleo", "gluten-free", "halal", "kosher"]
        )
    )
    goals = fields.List(fields.Str())


@profile_bp.post("/profile")
@jwt_required()
def create_or_update_profile():
    """Create or update the authenticated user's health profile."""
    schema = ProfileSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 422

    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    for key, value in data.items():
        setattr(profile, key, value)

    profile.bmi = profile.compute_bmi()
    db.session.commit()

    return jsonify({"message": "Profile saved", "profile": profile.to_dict()}), 200


@profile_bp.get("/profile")
@jwt_required()
def get_profile():
    """Retrieve the authenticated user's health profile."""
    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "Profile not found. Please set up your profile."}), 404
    return jsonify(profile.to_dict()), 200
