"""Application entry point."""
import os
from app import create_app, db
from app.utils.swagger import swagger_bp

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)
app.register_blueprint(swagger_bp, url_prefix="/api")


@app.cli.command("create-db")
def create_db():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("Database tables created.")


@app.cli.command("seed-db")
def seed_db():
    """Seed with sample products for testing."""
    from app.models.product import Product
    with app.app_context():
        if Product.query.count() == 0:
            sample = Product(
                barcode="737628064502",
                name="Organic Peanut Butter",
                brand="Smucker's",
                category="Spreads",
                ingredients_text="Organic Roasted Peanuts, Salt",
                nutrition_per_100g={"energy_kcal": 593, "proteins_g": 25, "fat_g": 50, "carbohydrates_g": 22, "sugars_g": 7, "sodium_mg": 100},
                is_vegetarian=True,
                is_vegan=True,
                nutriscore_grade="b",
                nova_group=2,
                allergens=["en:peanuts"],
            )
            db.session.add(sample)
            db.session.commit()
            print("Seeded sample products.")
        else:
            print("Database already has products, skipping seed.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
