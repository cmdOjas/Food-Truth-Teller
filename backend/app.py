"""
Food Truth Teller - Flask Backend
Simple SQLite-based REST API for personalized food analysis.
Run: python app.py
"""
import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "food_truth.db"
MODEL_PATH = BASE_DIR.parent / "ml" / "models" / "health_model.pkl"

# Load ML model at startup (fallback to rule-based if not found)
try:
    _clf = joblib.load(MODEL_PATH)
    ML_AVAILABLE = True
    print(f"[ML] Model loaded from {MODEL_PATH}")
except Exception as e:
    _clf = None
    ML_AVAILABLE = False
    print(f"[ML] Model not found ({e}), using rule-based analysis")

# ─────────────────────────────────────────────
# Seed products (20 real packaged foods)
# ─────────────────────────────────────────────
SEED_PRODUCTS = [
    {
        "barcode": "049000006346",
        "product_name": "Coca-Cola Classic",
        "brand": "Coca-Cola",
        "ingredients": "Carbonated Water, High Fructose Corn Syrup, Caramel Color, Phosphoric Acid, Natural Flavors, Caffeine",
        "category": "Beverages",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 10.6, "per_100g_sodium": 10.0,
        "image_url": "https://images.openfoodfacts.org/images/products/049/000/006/346/front_en.3.400.jpg",
    },
    {
        "barcode": "028400050845",
        "product_name": "Lay's Classic Potato Chips",
        "brand": "Frito-Lay",
        "ingredients": "Potatoes, Vegetable Oil (Sunflower, Corn, and/or Canola Oil), Salt",
        "category": "Snacks",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 0.5, "per_100g_sodium": 530.0,
        "image_url": "https://images.openfoodfacts.org/images/products/028/400/050/845/front_en.10.400.jpg",
    },
    {
        "barcode": "037466077260",
        "product_name": "Oreo Original Cookies",
        "brand": "Nabisco",
        "ingredients": "Unbleached Enriched Flour (Wheat Flour, Niacin, Reduced Iron, Thiamine Mononitrate, Riboflavin, Folic Acid), Sugar, Palm and/or Canola Oil, Cocoa (processed with alkali), High Fructose Corn Syrup, Leavening (Baking Soda and/or Calcium Phosphate), Salt, Soy Lecithin, Natural and Artificial Flavors",
        "category": "Biscuits & Cookies",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 42.0, "per_100g_sodium": 350.0,
        "image_url": "https://images.openfoodfacts.org/images/products/037/466/077/260/front_en.8.400.jpg",
    },
    {
        "barcode": "009800895452",
        "product_name": "Nutella Hazelnut Spread",
        "brand": "Ferrero",
        "ingredients": "Sugar, Palm Oil, Hazelnuts (13%), Skim Milk Powder (8.7%), Fat-Reduced Cocoa Powder, Soy Lecithin as Emulsifier, Vanillin",
        "category": "Spreads",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 56.3, "per_100g_sodium": 40.0,
        "image_url": "https://images.openfoodfacts.org/images/products/009/800/895/452/front_en.14.400.jpg",
    },
    {
        "barcode": "034000002405",
        "product_name": "Kit Kat Wafer Bar",
        "brand": "Nestle",
        "ingredients": "Sugar, Wheat Flour, Nonfat Milk, Cocoa Butter, Chocolate, Palm Kernel Oil, Lactose, Milk Fat, Contains 2% or Less of: Soy Lecithin, PGPR, Yeast, Sodium Bicarbonate, Salt, Natural Flavor, Vanillin",
        "category": "Chocolate",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 48.8, "per_100g_sodium": 85.0,
        "image_url": "https://images.openfoodfacts.org/images/products/034/000/002/405/front_en.5.400.jpg",
    },
    {
        "barcode": "030000010112",
        "product_name": "Quaker Old Fashioned Oats",
        "brand": "Quaker",
        "ingredients": "100% Whole Grain Rolled Oats",
        "category": "Cereals",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 1.1, "per_100g_sodium": 2.0,
        "image_url": "https://images.openfoodfacts.org/images/products/030/000/010/112/front_en.25.400.jpg",
    },
    {
        "barcode": "038000191008",
        "product_name": "Kellogg's Corn Flakes",
        "brand": "Kellogg's",
        "ingredients": "Milled Corn, Sugar, Malt Flavoring, Salt. Vitamins and Minerals: Ascorbic Acid (Vitamin C), Reduced Iron, Niacinamide, Zinc and Iron (Mineral Nutrients), Vitamin B6, Riboflavin (B2), Thiamin Hydrochloride (B1), Vitamin A Palmitate, Folic Acid, Vitamin D, Vitamin B12",
        "category": "Cereals",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 7.5, "per_100g_sodium": 270.0,
        "image_url": "https://images.openfoodfacts.org/images/products/038/000/191/008/front_en.8.400.jpg",
    },
    {
        "barcode": "048500014468",
        "product_name": "Tropicana Pure Premium Orange Juice",
        "brand": "Tropicana",
        "ingredients": "100% Pure Pasteurized Orange Juice",
        "category": "Juices",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 8.4, "per_100g_sodium": 1.0,
        "image_url": "https://images.openfoodfacts.org/images/products/048/500/014/468/front_en.6.400.jpg",
    },
    {
        "barcode": "040000465713",
        "product_name": "Snickers Bar",
        "brand": "Mars",
        "ingredients": "Milk Chocolate (Sugar, Cocoa Butter, Skim Milk, Chocolate, Lactose, Milkfat, Soy Lecithin, Artificial Flavor), Peanuts, Corn Syrup, Sugar, Palm Oil, Skim Milk, Lactose, Salt, Egg Whites, Chocolate, Artificial Flavor",
        "category": "Chocolate",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 47.5, "per_100g_sodium": 130.0,
        "image_url": "https://images.openfoodfacts.org/images/products/040/000/465/713/front_en.10.400.jpg",
    },
    {
        "barcode": "038000845598",
        "product_name": "Pringles Original",
        "brand": "Kellogg's",
        "ingredients": "Dried Potatoes, Vegetable Oil (Corn, Cottonseed, High Oleic Soybean, and/or Sunflower Oil), Degerminated Yellow Corn Flour, Cornstarch, Rice Flour, Maltodextrin, Mono- and Diglycerides, Salt, Wheat Starch, Dextrose",
        "category": "Snacks",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 1.0, "per_100g_sodium": 480.0,
        "image_url": "https://images.openfoodfacts.org/images/products/038/000/845/598/front_en.19.400.jpg",
    },
    {
        "barcode": "016000275591",
        "product_name": "Nature Valley Oats 'n Honey Granola Bar",
        "brand": "General Mills",
        "ingredients": "Whole Grain Oats, Sugar, Canola Oil, Honey, Salt, Soy Lecithin, Baking Soda",
        "category": "Snack Bars",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 28.0, "per_100g_sodium": 160.0,
        "image_url": "https://images.openfoodfacts.org/images/products/016/000/275/591/front_en.9.400.jpg",
    },
    {
        "barcode": "074684006085",
        "product_name": "Häagen-Dazs Vanilla Ice Cream",
        "brand": "Häagen-Dazs",
        "ingredients": "Cream, Skim Milk, Sugar, Egg Yolks, Vanilla Extract",
        "category": "Ice Cream",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 21.0, "per_100g_sodium": 55.0,
        "image_url": "https://images.openfoodfacts.org/images/products/074/684/006/085/front_en.7.400.jpg",
    },
    {
        "barcode": "028400090513",
        "product_name": "Doritos Nacho Cheese",
        "brand": "Frito-Lay",
        "ingredients": "Whole Corn, Vegetable Oil (Corn, Canola, and/or Sunflower Oil), Salt, Cheddar Cheese (Milk, Cheese Cultures, Salt, Enzymes), Maltodextrin, Whey, Monosodium Glutamate, Buttermilk, Romano Cheese, Whey Protein Concentrate, Onion Powder, Corn Flour, Natural and Artificial Flavor, Dextrose, Tomato Powder, Spice, Yellow 6, Yellow 5, Red 40, Lactic Acid, Citric Acid",
        "category": "Snacks",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 2.0, "per_100g_sodium": 490.0,
        "image_url": "https://images.openfoodfacts.org/images/products/028/400/090/513/front_en.12.400.jpg",
    },
    {
        "barcode": "611269997124",
        "product_name": "Red Bull Energy Drink",
        "brand": "Red Bull",
        "ingredients": "Carbonated Water, Sucrose, Glucose, Citric Acid, Taurine, Sodium Bicarbonate, Magnesium Carbonate, Caffeine, Niacinamide, Calcium Pantothenate, Pyridoxine HCl, Vitamin B12, Natural and Artificial Flavors, Colors (Caramel Color)",
        "category": "Energy Drinks",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 11.0, "per_100g_sodium": 40.0,
        "image_url": "https://images.openfoodfacts.org/images/products/611/269/997/124/front_en.7.400.jpg",
    },
    {
        "barcode": "040000002178",
        "product_name": "Kinder Bueno",
        "brand": "Ferrero",
        "ingredients": "Sugar, Wheat Flour, Palm Oil, Skim Milk Powder, Hazelnuts (10.5%), Cocoa, Cocoa Butter, Whole Milk Powder, Lactose and Proteins from Whey, Emulsifier (Soy Lecithin), Yeast, Natural Vanilla Flavoring, Eggs, Salt",
        "category": "Chocolate",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 46.0, "per_100g_sodium": 70.0,
        "image_url": "https://images.openfoodfacts.org/images/products/040/000/002/178/front_en.7.400.jpg",
    },
    {
        "barcode": "051000012631",
        "product_name": "Campbell's Condensed Tomato Soup",
        "brand": "Campbell's",
        "ingredients": "Tomato Puree (Water, Tomato Paste), Water, High Fructose Corn Syrup, Wheat Flour, Salt, Potassium Chloride, Flavoring, Citric Acid, Lower Sodium Natural Sea Salt",
        "category": "Soups",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 9.0, "per_100g_sodium": 480.0,
        "image_url": "https://images.openfoodfacts.org/images/products/051/000/012/631/front_en.8.400.jpg",
    },
    {
        "barcode": "013000003536",
        "product_name": "Heinz Tomato Ketchup",
        "brand": "Heinz",
        "ingredients": "Tomato Concentrate from Red Ripe Tomatoes, Distilled Vinegar, High Fructose Corn Syrup, Corn Syrup, Salt, Spice, Onion Powder, Natural Flavoring",
        "category": "Condiments",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 22.0, "per_100g_sodium": 920.0,
        "image_url": "https://images.openfoodfacts.org/images/products/013/000/003/536/front_en.9.400.jpg",
    },
    {
        "barcode": "021000014897",
        "product_name": "Philadelphia Original Cream Cheese",
        "brand": "Kraft",
        "ingredients": "Pasteurized Milk and Cream, Salt, Carob Bean Gum",
        "category": "Dairy",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 2.7, "per_100g_sodium": 320.0,
        "image_url": "https://images.openfoodfacts.org/images/products/021/000/014/897/front_en.12.400.jpg",
    },
    {
        "barcode": "036632030375",
        "product_name": "Activia Strawberry Yogurt",
        "brand": "Dannon",
        "ingredients": "Cultured Pasteurized Grade A Reduced Fat Milk, Water, Strawberries, Sugar, Modified Corn Starch, Fructose, Tricalcium Phosphate, Natural Flavor, Carmine (Color), Potassium Sorbate, Malic Acid, Sucralose, Acesulfame Potassium, Vitamin D3, L. acidophilus, Bifidus Regularis",
        "category": "Dairy",
        "is_vegetarian": 1, "is_vegan": 0,
        "per_100g_sugar": 11.2, "per_100g_sodium": 65.0,
        "image_url": "https://images.openfoodfacts.org/images/products/036/632/030/375/front_en.7.400.jpg",
    },
    {
        "barcode": "016000394605",
        "product_name": "Fiber One Original Bran Cereal",
        "brand": "General Mills",
        "ingredients": "Whole Grain Wheat, Corn Bran, Modified Wheat Starch, Guar Gum, Salt, Baking Soda, Sucralose, BHT Added to Packaging Material to Preserve Freshness",
        "category": "Cereals",
        "is_vegetarian": 1, "is_vegan": 1,
        "per_100g_sugar": 0.0, "per_100g_sodium": 230.0,
        "image_url": "https://images.openfoodfacts.org/images/products/016/000/394/605/front_en.8.400.jpg",
    },
]


# ─────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            age         INTEGER,
            gender      TEXT,
            weight      REAL,
            diseases    TEXT DEFAULT '[]',
            allergies   TEXT DEFAULT '[]',
            diet_type   TEXT DEFAULT 'non-vegetarian',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS products (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode         TEXT UNIQUE NOT NULL,
            product_name    TEXT NOT NULL,
            brand           TEXT,
            ingredients     TEXT,
            category        TEXT,
            is_vegetarian   INTEGER DEFAULT 0,
            is_vegan        INTEGER DEFAULT 0,
            per_100g_sugar  REAL DEFAULT 0,
            per_100g_sodium REAL DEFAULT 0,
            image_url       TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()

    # Seed products if empty
    cur = conn.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        for p in SEED_PRODUCTS:
            conn.execute(
                """INSERT INTO products
                   (barcode,product_name,brand,ingredients,category,
                    is_vegetarian,is_vegan,per_100g_sugar,per_100g_sodium,image_url)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (p["barcode"], p["product_name"], p["brand"], p["ingredients"],
                 p["category"], p["is_vegetarian"], p["is_vegan"],
                 p["per_100g_sugar"], p["per_100g_sodium"], p["image_url"]),
            )
        conn.commit()
        print(f"[DB] Seeded {len(SEED_PRODUCTS)} products")

    conn.close()


def row_to_dict(row):
    return dict(row) if row else None


# ─────────────────────────────────────────────
# Ingredient presence checkers (for zero-tolerance / allergy logic)
# ─────────────────────────────────────────────
_ING = {
    "gluten":        ["wheat", "barley", "rye", "gluten", "semolina", "spelt", "kamut", "malt"],
    "dairy":         ["milk", "cream", "cheese", "butter", "whey", "casein", "lactose", "skim milk"],
    "nuts":          ["peanut", "almond", "cashew", "walnut", "hazelnut", "pecan", "pistachio", "macadamia"],
    "soy":           ["soy", "soya", "soybean"],
    "egg":           ["egg", "albumin", "ovalbumin"],
    "trans_fat":     ["partially hydrogenated", "trans fat"],
    "preservatives": ["sodium benzoate", "potassium sorbate", "bha", "bht", "tbhq"],
    "colors":        ["red 40", "yellow 5", "yellow 6", "blue 1", "tartrazine", "sunset yellow"],
    "caffeine":      ["caffeine", "guarana", "coffee extract"],
    "msg":           ["monosodium glutamate", " msg", "e621"],
    "sweeteners":    ["aspartame", "sucralose", "saccharin", "acesulfame"],
    "animal":        ["gelatin", "lard", "tallow", "rennet", "carmine", "isinglass"],
}

def _has(text: str, key: str) -> bool:
    return any(kw in text for kw in _ING[key])


# ─────────────────────────────────────────────
# Quantity-based thresholds (WHO / ADA / AHA / FDA)
# Per 100 g of product — source: LabelSafe Ingredient Health Reference
# ─────────────────────────────────────────────
# Sugar (g / 100 g)
#   Default  : caution ≥10 g, avoid ≥20 g  (WHO: free sugars <10 % of energy)
#   Diabetes : caution ≥5 g,  avoid ≥10 g  (ADA: ≤10 g added sugar per snack)
_SUGAR = {
    "default":  {"caution": 10.0, "avoid": 20.0},
    "diabetes": {"caution":  5.0, "avoid": 10.0},
}

# Sodium (mg / 100 g)
#   Default      : caution ≥400 mg, avoid ≥1000 mg  (WHO: ≤2000 mg/day)
#   Hypertension : caution ≥200 mg, avoid ≥400 mg   (AHA ideal: ≤1500 mg/day)
#   Kidney       : same as hypertension              (ESH CKD guidance)
_SODIUM = {
    "default":      {"caution": 400.0, "avoid": 1000.0},
    "hypertension": {"caution": 200.0, "avoid":  400.0},
    "kidney":       {"caution": 200.0, "avoid":  400.0},
}


# ─────────────────────────────────────────────
# Unified threshold-based rating engine
# ─────────────────────────────────────────────
def rate_product(product_data: dict, profile: dict) -> tuple:
    """
    Returns (rating, confidence, probabilities, reasons).

    Rating tiers (per LabelSafe reference, Section 4):
      safe    — all nutrients below caution threshold, no zero-tolerance hits
      caution — a nutrient exceeds caution but not avoid threshold, or
                lactose intolerance + dairy present
      avoid   — a nutrient exceeds avoid threshold, OR zero-tolerance ingredient
                present (gluten for celiac, allergen for allergy profile)
    """
    text = (product_data.get("ingredients") or "").lower()
    sugar_g  = float(product_data.get("per_100g_sugar")  or 0)
    sodium_mg = float(product_data.get("per_100g_sodium") or 0)

    diseases  = [d.lower() for d in (profile.get("diseases")  or [])]
    allergies = [a.lower() for a in (profile.get("allergies") or [])]
    diet      = (profile.get("diet_type") or "non-vegetarian").lower()

    def has_d(*keys): return any(k in d for k in keys for d in diseases)
    def has_a(*keys): return any(k in a for k in keys for a in allergies)

    levels  = []   # 0=safe, 1=caution, 2=avoid
    reasons = []

    # ── 1. Zero-tolerance: celiac / gluten allergy ──────────────────────────
    if _has(text, "gluten"):
        if has_d("celiac"):
            levels.append(2)
            reasons.append("🚫 Contains gluten — zero-tolerance for celiac disease (wheat / barley / rye / malt)")
        if has_a("gluten"):
            levels.append(2)
            reasons.append("🚫 Contains gluten — you have a gluten allergy")

    # ── 2. Zero-tolerance: nut allergy ──────────────────────────────────────
    if _has(text, "nuts") and has_a("nut", "peanut"):
        levels.append(2)
        reasons.append("🚫 Contains nuts — you have a nut allergy (anaphylaxis risk)")

    # ── 3. Zero-tolerance: dairy allergy vs. lactose intolerance ────────────
    if _has(text, "dairy"):
        if has_a("dairy"):
            levels.append(2)
            reasons.append("🚫 Contains dairy — you have a dairy allergy")
        elif has_d("lactose"):
            # Section 3.6: lactose tolerance is individual → Caution, not Avoid
            levels.append(1)
            reasons.append("⚠️ Contains dairy/lactose — caution if lactose intolerant (individual tolerance varies; consider lactase supplements)")

    # ── 4. Zero-tolerance: soy allergy ──────────────────────────────────────
    if _has(text, "soy") and has_a("soy"):
        levels.append(2)
        reasons.append("🚫 Contains soy — you have a soy allergy")

    # ── 5. Zero-tolerance: egg allergy ──────────────────────────────────────
    if _has(text, "egg") and has_a("egg"):
        levels.append(2)
        reasons.append("🚫 Contains eggs — you have an egg allergy")

    # ── 6. Sugar — quantity-based (g / 100 g) ───────────────────────────────
    is_diabetic    = has_d("diabetes")
    sugar_thresh   = _SUGAR["diabetes"] if is_diabetic else _SUGAR["default"]
    condition_label = "diabetes" if is_diabetic else "general"

    if sugar_g >= sugar_thresh["avoid"]:
        levels.append(2)
        reasons.append(
            f"🚫 Very high sugar ({sugar_g:.1f} g/100 g) — exceeds {condition_label} avoid threshold "
            f"({sugar_thresh['avoid']:.0f} g/100 g)"
        )
    elif sugar_g >= sugar_thresh["caution"]:
        levels.append(1)
        reasons.append(
            f"⚠️ Elevated sugar ({sugar_g:.1f} g/100 g) — above {condition_label} caution threshold "
            f"({sugar_thresh['caution']:.0f} g/100 g)"
        )

    # ── 7. Sodium — quantity-based (mg / 100 g) ─────────────────────────────
    is_hypertensive = has_d("bp", "blood pressure", "hypertension")
    has_kidney      = has_d("kidney")
    if is_hypertensive or has_kidney:
        sodium_thresh  = _SODIUM["kidney"] if has_kidney else _SODIUM["hypertension"]
        sodium_label   = "kidney disease" if has_kidney else "hypertension"
    else:
        sodium_thresh  = _SODIUM["default"]
        sodium_label   = "general"

    if sodium_mg >= sodium_thresh["avoid"]:
        levels.append(2)
        reasons.append(
            f"🚫 Very high sodium ({sodium_mg:.0f} mg/100 g) — exceeds {sodium_label} avoid threshold "
            f"({sodium_thresh['avoid']:.0f} mg/100 g)"
        )
    elif sodium_mg >= sodium_thresh["caution"]:
        levels.append(1)
        reasons.append(
            f"⚠️ High sodium ({sodium_mg:.0f} mg/100 g) — above {sodium_label} caution threshold "
            f"({sodium_thresh['caution']:.0f} mg/100 g)"
        )

    # ── 8. Trans fat — presence-based (no safe threshold per FDA) ───────────
    if _has(text, "trans_fat"):
        if has_d("heart"):
            levels.append(2)
            reasons.append("🚫 Contains trans fat — avoid with heart disease (AHA: no safe level)")
        else:
            levels.append(1)
            reasons.append("⚠️ Contains partially hydrogenated / trans fat — associated with cardiovascular risk")

    # ── 9. Other ingredient cautions ────────────────────────────────────────
    if _has(text, "preservatives"):
        levels.append(1)
        reasons.append("⚠️ Contains artificial preservatives (BHA / BHT / sodium benzoate)")

    if _has(text, "colors"):
        levels.append(1)
        reasons.append("⚠️ Contains artificial food dyes (Red 40 / Yellow 5 / Yellow 6)")

    if _has(text, "caffeine"):
        if has_d("heart"):
            levels.append(1)
            reasons.append("⚠️ Contains caffeine — use caution with heart conditions")
        else:
            reasons.append("ℹ️ Contains caffeine — be mindful if sensitive or pregnant")

    if _has(text, "msg"):
        reasons.append("ℹ️ Contains MSG — may cause sensitivity in some people")

    if _has(text, "sweeteners"):
        reasons.append("ℹ️ Contains artificial sweeteners — generally recognised as safe in moderation")

    # ── 10. Diet-type checks ────────────────────────────────────────────────
    if _has(text, "animal"):
        if diet == "vegan":
            levels.append(1)
            reasons.append("⚠️ Contains animal-derived ingredients (gelatin / carmine / lard) — not vegan")
        elif diet == "vegetarian":
            reasons.append("ℹ️ May contain animal-derived ingredients — verify if suitable for vegetarians")

    # ── Aggregate ────────────────────────────────────────────────────────────
    worst = max(levels) if levels else 0
    if worst == 2:
        rating      = "avoid"
        confidence  = 0.93
        proba       = [0.03, 0.04, 0.93]
    elif worst == 1:
        rating      = "caution"
        confidence  = 0.82
        proba       = [0.13, 0.82, 0.05]
    else:
        rating      = "safe"
        confidence  = 0.90
        proba       = [0.90, 0.07, 0.03]
        reasons     = [
            "✅ All nutrient levels within safe thresholds for your health profile",
            "No allergens, zero-tolerance ingredients, or excessive sugar / sodium detected",
        ]

    return rating, confidence, proba, reasons


# ─────────────────────────────────────────────
# OpenFoodFacts fallback
# ─────────────────────────────────────────────
def fetch_from_openfoodfacts(barcode: str) -> dict | None:
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "FoodTruthTeller/1.0"})
        data = resp.json()
        if data.get("status") != 1:
            return None
        p = data["product"]
        nutriments = p.get("nutriments", {})
        return {
            "barcode": barcode,
            "product_name": p.get("product_name") or p.get("product_name_en") or "Unknown Product",
            "brand": p.get("brands", "Unknown"),
            "ingredients": p.get("ingredients_text_en") or p.get("ingredients_text", ""),
            "category": p.get("categories", "").split(",")[0].strip() if p.get("categories") else "Other",
            "is_vegetarian": int("en:vegetarian" in p.get("labels_tags", [])),
            "is_vegan": int("en:vegan" in p.get("labels_tags", [])),
            "per_100g_sugar": float(nutriments.get("sugars_100g") or 0),
            "per_100g_sodium": float(nutriments.get("sodium_100g") or 0) * 1000,  # kg→mg
            "image_url": p.get("image_front_url") or p.get("image_url", ""),
        }
    except Exception as e:
        print(f"[OFF] Error fetching {barcode}: {e}")
        return None


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.route("/api/user/profile", methods=["POST"])
def create_or_update_profile():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    diseases  = json.dumps(data.get("diseases", []))
    allergies = json.dumps(data.get("allergies", []))

    user_id = data.get("user_id")
    conn = get_db()
    if user_id:
        conn.execute(
            """UPDATE users SET name=?,age=?,gender=?,weight=?,diseases=?,allergies=?,diet_type=?
               WHERE id=?""",
            (name, data.get("age"), data.get("gender"), data.get("weight"),
             diseases, allergies, data.get("diet_type", "non-vegetarian"), user_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    else:
        cur = conn.execute(
            """INSERT INTO users (name,age,gender,weight,diseases,allergies,diet_type)
               VALUES (?,?,?,?,?,?,?)""",
            (name, data.get("age"), data.get("gender"), data.get("weight"),
             diseases, allergies, data.get("diet_type", "non-vegetarian")),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()

    user = row_to_dict(row)
    user["diseases"]  = json.loads(user["diseases"] or "[]")
    user["allergies"] = json.loads(user["allergies"] or "[]")
    return jsonify({"user": user}), 200


@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "User not found"}), 404
    user = row_to_dict(row)
    user["diseases"]  = json.loads(user["diseases"] or "[]")
    user["allergies"] = json.loads(user["allergies"] or "[]")
    return jsonify({"user": user}), 200


@app.route("/api/products", methods=["GET"])
def list_products():
    conn = get_db()
    rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    products = [row_to_dict(r) for r in rows]
    return jsonify({"products": products, "total": len(products)}), 200


@app.route("/api/product/<barcode>", methods=["GET"])
def get_product(barcode):
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE barcode=?", (barcode,)).fetchone()
    conn.close()
    if row:
        return jsonify({"product": row_to_dict(row), "source": "local"}), 200

    # Try Open Food Facts
    product_data = fetch_from_openfoodfacts(barcode)
    if not product_data:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404

    # Cache in DB
    conn = get_db()
    conn.execute(
        """INSERT OR IGNORE INTO products
           (barcode,product_name,brand,ingredients,category,is_vegetarian,is_vegan,per_100g_sugar,per_100g_sodium,image_url)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (product_data["barcode"], product_data["product_name"], product_data["brand"],
         product_data["ingredients"], product_data["category"], product_data["is_vegetarian"],
         product_data["is_vegan"], product_data["per_100g_sugar"], product_data["per_100g_sodium"],
         product_data["image_url"]),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM products WHERE barcode=?", (barcode,)).fetchone()
    conn.close()
    return jsonify({"product": row_to_dict(row), "source": "openfoodfacts"}), 200


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    barcode  = data.get("barcode")

    if not user_id or not barcode:
        return jsonify({"error": "user_id and barcode are required"}), 400

    conn = get_db()
    user_row    = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    product_row = conn.execute("SELECT * FROM products WHERE barcode=?", (barcode,)).fetchone()
    conn.close()

    if not user_row:
        return jsonify({"error": "User not found"}), 404

    product_data = row_to_dict(product_row) if product_row else None
    if not product_data:
        # Try fetching
        product_data = fetch_from_openfoodfacts(barcode)
        if not product_data:
            return jsonify({"error": f"Product {barcode} not found"}), 404

    profile = row_to_dict(user_row)
    profile["diseases"]  = json.loads(profile["diseases"] or "[]")
    profile["allergies"] = json.loads(profile["allergies"] or "[]")

    rating, confidence, probabilities, reasons = rate_product(product_data, profile)

    return jsonify({
        "rating":        rating,
        "confidence":    confidence,
        "probabilities": {
            "safe":    round(probabilities[0], 3),
            "caution": round(probabilities[1], 3),
            "avoid":   round(probabilities[2], 3),
        },
        "reasons":   reasons,
        "product":   product_data,
        "user_name": profile["name"],
        "ml_used":   False,
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    message = (data.get("message") or "").lower().strip()
    product_barcode = data.get("product_barcode")

    if not user_id:
        return jsonify({"response": "Please set up your profile first to use the chatbot."}), 400

    conn = get_db()
    user_row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()

    if not user_row:
        return jsonify({"response": "Profile not found. Please create your profile first."}), 404

    profile = row_to_dict(user_row)
    profile["diseases"]  = json.loads(profile["diseases"] or "[]")
    profile["allergies"] = json.loads(profile["allergies"] or "[]")

    name      = profile["name"]
    diseases  = profile["diseases"]
    allergies = profile["allergies"]
    diet      = profile.get("diet_type", "non-vegetarian")

    # Pattern-based responses
    response = _generate_chat_response(message, name, diseases, allergies, diet, product_barcode, profile)
    return jsonify({"response": response, "timestamp": datetime.utcnow().isoformat()}), 200


def _generate_chat_response(message, name, diseases, allergies, diet, product_barcode, profile):
    # Greeting
    if any(w in message for w in ["hello", "hi", "hey", "namaste"]):
        cond_str = ", ".join(diseases) if diseases else "none"
        return (f"Hello {name}! 👋 I'm your Food Truth Teller assistant.\n\n"
                f"Your health conditions: **{cond_str}**\n"
                f"Allergies: **{', '.join(allergies) if allergies else 'none'}**\n\n"
                f"Scan a product or ask me anything about food and your health!")

    # About scanned product
    if product_barcode and any(w in message for w in ["safe", "eat", "okay", "ok", "good", "bad"]):
        conn = get_db()
        row = conn.execute("SELECT * FROM products WHERE barcode=?", (product_barcode,)).fetchone()
        conn.close()
        if row:
            product = row_to_dict(row)
            rating, _, _, reasons = rate_product(product, profile)
            reasons_str = "\n".join(f"• {r}" for r in reasons[:4])
            emoji = {"safe": "✅", "caution": "⚠️", "avoid": "🚫"}.get(rating, "")
            return (f"For **{product['product_name']}** — Rating: **{rating.upper()}** {emoji}\n\n"
                    f"{reasons_str}")

    # Diabetes
    if "diabetes" in message or "sugar" in message:
        if "diabetes" in diseases:
            return ("As someone with **diabetes**, here's what to watch for:\n\n"
                    "• 🚫 **Avoid**: products with sugar, high fructose corn syrup, dextrose, maltose\n"
                    "• ✅ **Prefer**: whole grains, vegetables, lean proteins\n"
                    "• ⚠️ Artificial sweeteners (sucralose, aspartame) are okay in moderation\n"
                    "• Target < 5g sugar per 100g for most packaged foods")
        return ("**Sugar tips for everyone:**\n\n"
                "• The WHO recommends < 25g of free sugars per day\n"
                "• Watch out for hidden sugars: corn syrup, dextrose, fructose, maltose\n"
                "• Choose products with < 5g sugar per 100g when possible")

    # Allergies
    if "allerg" in message:
        if allergies:
            allergy_list = "\n".join(f"• **{a.title()}** — always check labels for derivatives" for a in allergies)
            return (f"You have listed these allergies:\n\n{allergy_list}\n\n"
                    "I scan for these in every product you check. For severe allergies, "
                    "always verify the 'Contains' and 'May Contain' sections on labels.")
        return ("No allergies in your profile. You can update your profile to add any allergies "
                "and I'll flag them in every product scan.")

    # Blood pressure
    if any(w in message for w in ["blood pressure", "bp", "sodium", "salt", "hypertension"]):
        if any(d in diseases for d in ["bp", "blood pressure", "hypertension"]):
            return ("For **high blood pressure** management:\n\n"
                    "• 🚫 Limit sodium to < 1500mg/day\n"
                    "• Watch out for: processed foods, canned soups, pickles, soy sauce\n"
                    "• ✅ Choose: fresh fruits, vegetables, whole grains, potassium-rich foods\n"
                    "• Any product with > 600mg sodium per 100g is high-sodium")
        return ("**Sodium guidelines:**\n\nThe WHO recommends < 2000mg sodium per day. "
                "Aim for products with < 120mg sodium per 100g (low sodium).")

    # Heart / cardiovascular
    if any(w in message for w in ["heart", "cholesterol", "cardiovascular"]):
        return ("**Heart-healthy eating tips:**\n\n"
                "• 🚫 Avoid trans fats (hydrogenated/partially hydrogenated oils)\n"
                "• ⚠️ Limit saturated fat and processed meats\n"
                "• ✅ Choose: olive oil, nuts, fish, whole grains, vegetables\n"
                "• I flag products with trans fat as Avoid if you have heart conditions")

    # Celiac / gluten
    if any(w in message for w in ["celiac", "gluten", "wheat"]):
        if "celiac" in diseases or "gluten" in allergies:
            return ("For **celiac disease / gluten intolerance:**\n\n"
                    "• 🚫 Strictly avoid: wheat, barley, rye, spelt, kamut, semolina\n"
                    "• ⚠️ Watch for hidden gluten: malt, modified food starch, soy sauce\n"
                    "• ✅ Safe grains: rice, quinoa, corn, oats (certified GF only)\n"
                    "• I flag all gluten-containing products as Avoid for you")
        return ("**Gluten info:**\n\nGluten is found in wheat, barley, and rye. "
                "Only people with celiac disease or gluten sensitivity need to strictly avoid it.")

    # Vegetarian / vegan
    if any(w in message for w in ["vegetarian", "vegan", "meat", "animal"]):
        if diet == "vegan":
            return ("As a **vegan**, I flag:\n\n"
                    "• 🚫 Gelatin (animal bones)\n• 🚫 Carmine (red dye from insects)\n"
                    "• 🚫 Casein/whey (dairy proteins)\n• 🚫 Isinglass (fish)\n"
                    "• 🚫 Lard/tallow (animal fat)\n\n"
                    "Tip: Look for certified vegan labels for extra assurance!")
        if diet == "vegetarian":
            return ("As a **vegetarian**, watch for:\n\n"
                    "• ⚠️ Gelatin (in marshmallows, gummy bears, jello)\n"
                    "• ⚠️ Rennet in some cheeses\n"
                    "• ⚠️ Carmine (E120) used as red coloring\n"
                    "• ⚠️ Some omega-3 supplements derived from fish")

    # Ingredients question
    if "ingredient" in message or "what" in message:
        return ("I analyze products for:\n\n"
                "🍬 **High sugar** — harmful for diabetics\n"
                "🧂 **High sodium** — harmful for BP/kidney patients\n"
                "🌾 **Gluten** — harmful for celiac patients\n"
                "🥛 **Dairy** — harmful for lactose intolerant\n"
                "🥜 **Nuts** — flagged for nut allergy sufferers\n"
                "🎨 **Artificial colors** — Red 40, Yellow 5/6\n"
                "🧪 **Preservatives** — BHA, BHT, sodium benzoate\n"
                "⚗️ **Trans fat** — harmful for heart patients\n\n"
                "Scan a product to get your personalized rating!")

    # Default
    return (f"Hi {name}! 🌿 I'm here to help you make healthier food choices.\n\n"
            "Try asking me:\n"
            "• \"Is this product safe for me?\"\n"
            "• \"What should I avoid with diabetes?\"\n"
            "• \"Tell me about my allergies\"\n"
            "• \"What are healthy alternatives?\"\n\n"
            "Or scan a product barcode to get your personalized analysis!")


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "ml_available": ML_AVAILABLE}), 200


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    print(f"[Server] Starting on http://localhost:{port}")
    print(f"[Server] ML model: {'loaded' if ML_AVAILABLE else 'rule-based fallback'}")
    app.run(host="0.0.0.0", port=port, debug=debug)
