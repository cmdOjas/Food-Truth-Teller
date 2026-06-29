"""Open Food Facts API integration with local DB caching."""
import os
import requests
from typing import Optional
from flask import current_app
from app import db
from app.models.product import Product


class OpenFoodFactsService:
    """Fetches product data from the Open Food Facts v2 API and persists it locally."""

    BASE_URL = "https://world.openfoodfacts.org/api/v2"

    def fetch_and_store(self, barcode: str) -> Optional[Product]:
        """Fetch a product by barcode and save to the local database."""
        data = self._fetch(barcode)
        if not data:
            return None
        return self._upsert(barcode, data)

    def _fetch(self, barcode: str) -> Optional[dict]:
        try:
            url = f"{self.BASE_URL}/product/{barcode}"
            resp = requests.get(
                url,
                params={"fields": "product_name,brands,categories,ingredients_text,ingredients,nutriments,image_url,labels,allergens_tags,additives_tags,nutriscore_grade,nova_group,labels_tags"},
                timeout=10,
                headers={"User-Agent": "FoodTruthTeller/1.0"},
            )
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("status") == 1:
                return payload.get("product", {})
        except Exception as exc:
            current_app.logger.warning("OpenFoodFacts fetch failed for %s: %s", barcode, exc)
        return None

    def _upsert(self, barcode: str, data: dict) -> Product:
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            product = Product(barcode=barcode)
            db.session.add(product)

        nutriments = data.get("nutriments", {})
        nutrition = {
            "energy_kcal": nutriments.get("energy-kcal_100g"),
            "proteins_g": nutriments.get("proteins_100g"),
            "carbohydrates_g": nutriments.get("carbohydrates_100g"),
            "sugars_g": nutriments.get("sugars_100g"),
            "fat_g": nutriments.get("fat_100g"),
            "saturated_fat_g": nutriments.get("saturated-fat_100g"),
            "fiber_g": nutriments.get("fiber_100g"),
            "sodium_mg": nutriments.get("sodium_100g", 0) * 1000 if nutriments.get("sodium_100g") else None,
            "salt_g": nutriments.get("salt_100g"),
        }

        ingredients_parsed = []
        for ing in data.get("ingredients", []):
            if ing.get("text"):
                ingredients_parsed.append({"text": ing["text"], "id": ing.get("id", "")})

        labels = data.get("labels_tags", [])
        product.name = data.get("product_name") or "Unknown Product"
        product.brand = data.get("brands", "").split(",")[0].strip() if data.get("brands") else None
        product.category = data.get("categories", "").split(",")[0].strip() if data.get("categories") else None
        product.ingredients_text = data.get("ingredients_text", "")
        product.ingredients_parsed = ingredients_parsed
        product.nutrition_per_100g = nutrition
        product.image_url = data.get("image_url")
        product.is_vegetarian = "en:vegetarian" in labels
        product.is_vegan = "en:vegan" in labels
        product.nutriscore_grade = data.get("nutriscore_grade", "").lower() or None
        product.nova_group = data.get("nova_group")
        product.allergens = data.get("allergens_tags", [])
        product.additives = data.get("additives_tags", [])
        product.labels = labels
        product.source = "openfoodfacts"

        db.session.commit()
        return product
