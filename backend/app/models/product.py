"""Food product model."""
from datetime import datetime, timezone
from sqlalchemy import JSON
from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    brand = db.Column(db.String(255))
    category = db.Column(db.String(255))
    ingredients_text = db.Column(db.Text)
    ingredients_parsed = db.Column(JSON, default=list)
    nutrition_per_100g = db.Column(JSON, default=dict)
    image_url = db.Column(db.String(1000))
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    nutriscore_grade = db.Column(db.String(1))
    nova_group = db.Column(db.Integer)
    allergens = db.Column(JSON, default=list)
    additives = db.Column(JSON, default=list)
    labels = db.Column(JSON, default=list)
    source = db.Column(db.String(50), default="openfoodfacts")
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "barcode": self.barcode,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "ingredients_text": self.ingredients_text,
            "ingredients_parsed": self.ingredients_parsed or [],
            "nutrition_per_100g": self.nutrition_per_100g or {},
            "image_url": self.image_url,
            "is_vegetarian": self.is_vegetarian,
            "is_vegan": self.is_vegan,
            "nutriscore_grade": self.nutriscore_grade,
            "nova_group": self.nova_group,
            "allergens": self.allergens or [],
            "additives": self.additives or [],
            "labels": self.labels or [],
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Product {self.barcode} - {self.name}>"
