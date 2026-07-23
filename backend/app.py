"""
EatWise AI - Flask Backend
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

# Offline nutrition chatbot engine (no LLM / no external API)
from chatbot import engine as chat_engine
from chatbot import memory as chat_memory

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
# Extra per-100g nutrients for the seed products, used ONLY by the
# Nutri-Score calculator. Keyed by barcode so this stays additive and does
# not touch the existing SEED_PRODUCTS entries or any existing feature.
#   (energy_kj, saturated_fat_g, fiber_g, protein_g, fruits_veg_percent)
# ─────────────────────────────────────────────
SEED_NUTRIENTS = {
    "049000006346": {"energy_kj": 180.0,  "sat_fat": 0.0,  "fiber": 0.0,  "protein": 0.0,  "fruits_veg": 0.0},   # Coca-Cola
    "028400050845": {"energy_kj": 2250.0, "sat_fat": 3.0,  "fiber": 4.0,  "protein": 6.5,  "fruits_veg": 0.0},   # Lay's Chips
    "037466077260": {"energy_kj": 2050.0, "sat_fat": 5.0,  "fiber": 2.5,  "protein": 4.5,  "fruits_veg": 0.0},   # Oreo
    "009800895452": {"energy_kj": 2250.0, "sat_fat": 12.0, "fiber": 3.5,  "protein": 6.0,  "fruits_veg": 13.0},  # Nutella
    "034000002405": {"energy_kj": 2100.0, "sat_fat": 13.0, "fiber": 1.5,  "protein": 6.0,  "fruits_veg": 0.0},   # Kit Kat
    "030000010112": {"energy_kj": 1560.0, "sat_fat": 1.3,  "fiber": 10.0, "protein": 13.0, "fruits_veg": 0.0},   # Quaker Oats
    "038000191008": {"energy_kj": 1580.0, "sat_fat": 0.1,  "fiber": 3.0,  "protein": 7.0,  "fruits_veg": 0.0},   # Corn Flakes
    "048500014468": {"energy_kj": 190.0,  "sat_fat": 0.0,  "fiber": 0.5,  "protein": 0.7,  "fruits_veg": 100.0}, # Tropicana OJ
    "040000465713": {"energy_kj": 2000.0, "sat_fat": 9.0,  "fiber": 2.0,  "protein": 8.0,  "fruits_veg": 10.0},  # Snickers
    "038000845598": {"energy_kj": 2100.0, "sat_fat": 9.0,  "fiber": 3.5,  "protein": 4.0,  "fruits_veg": 0.0},   # Pringles
    "016000275591": {"energy_kj": 1900.0, "sat_fat": 1.5,  "fiber": 5.5,  "protein": 6.5,  "fruits_veg": 0.0},   # Nature Valley
    "074684006085": {"energy_kj": 1200.0, "sat_fat": 18.0, "fiber": 0.0,  "protein": 5.0,  "fruits_veg": 0.0},   # Häagen-Dazs
    "028400090513": {"energy_kj": 2150.0, "sat_fat": 4.5,  "fiber": 4.0,  "protein": 7.0,  "fruits_veg": 0.0},   # Doritos
    "611269997124": {"energy_kj": 190.0,  "sat_fat": 0.0,  "fiber": 0.0,  "protein": 0.0,  "fruits_veg": 0.0},   # Red Bull
    "040000002178": {"energy_kj": 2400.0, "sat_fat": 18.0, "fiber": 3.0,  "protein": 8.5,  "fruits_veg": 11.0},  # Kinder Bueno
    "051000012631": {"energy_kj": 300.0,  "sat_fat": 0.5,  "fiber": 1.0,  "protein": 1.5,  "fruits_veg": 40.0},  # Campbell's Soup
    "013000003536": {"energy_kj": 490.0,  "sat_fat": 0.1,  "fiber": 1.0,  "protein": 1.2,  "fruits_veg": 90.0},  # Heinz Ketchup
    "021000014897": {"energy_kj": 1350.0, "sat_fat": 20.0, "fiber": 0.0,  "protein": 6.0,  "fruits_veg": 0.0},   # Philadelphia
    "036632030375": {"energy_kj": 400.0,  "sat_fat": 1.0,  "fiber": 0.5,  "protein": 3.5,  "fruits_veg": 5.0},   # Activia
    "016000394605": {"energy_kj": 850.0,  "sat_fat": 0.5,  "fiber": 40.0, "protein": 8.0,  "fruits_veg": 0.0},   # Fiber One
}


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
            sensitivity TEXT DEFAULT 'medium',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS products (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode            TEXT UNIQUE NOT NULL,
            product_name       TEXT NOT NULL,
            brand              TEXT,
            ingredients        TEXT,
            category           TEXT,
            is_vegetarian      INTEGER DEFAULT 0,
            is_vegan           INTEGER DEFAULT 0,
            per_100g_sugar     REAL DEFAULT 0,
            per_100g_sodium    REAL DEFAULT 0,
            per_100g_energy_kj REAL DEFAULT 0,
            per_100g_sat_fat   REAL DEFAULT 0,
            per_100g_fiber     REAL DEFAULT 0,
            per_100g_protein   REAL DEFAULT 0,
            fruits_veg_percent REAL DEFAULT 0,
            image_url          TEXT,
            created_at         TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            barcode     TEXT NOT NULL DEFAULT 'general',
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            intent      TEXT,
            rating      TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_chat_user_barcode
            ON chat_messages (user_id, barcode, id);
    """)
    conn.commit()

    # Migration: add sensitivity column for DBs created before this feature
    user_cols = [r["name"] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "sensitivity" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN sensitivity TEXT DEFAULT 'medium'")
        conn.commit()
        print("[DB] Migrated: added sensitivity column to users table")

    # Migration: add Nutri-Score nutrient columns for DBs created before this feature
    product_cols = [r["name"] for r in conn.execute("PRAGMA table_info(products)").fetchall()]
    _nutri_cols = [
        "per_100g_energy_kj", "per_100g_sat_fat", "per_100g_fiber",
        "per_100g_protein", "fruits_veg_percent",
    ]
    _added_nutri = False
    for col in _nutri_cols:
        if col not in product_cols:
            conn.execute(f"ALTER TABLE products ADD COLUMN {col} REAL DEFAULT 0")
            _added_nutri = True
    if _added_nutri:
        conn.commit()
        # Backfill seed products with their known nutrient values
        for barcode, n in SEED_NUTRIENTS.items():
            conn.execute(
                """UPDATE products SET per_100g_energy_kj=?, per_100g_sat_fat=?,
                       per_100g_fiber=?, per_100g_protein=?, fruits_veg_percent=?
                   WHERE barcode=?""",
                (n["energy_kj"], n["sat_fat"], n["fiber"], n["protein"], n["fruits_veg"], barcode),
            )
        conn.commit()
        print("[DB] Migrated: added Nutri-Score nutrient columns and backfilled seed products")

    # Seed products if empty
    cur = conn.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        for p in SEED_PRODUCTS:
            n = SEED_NUTRIENTS.get(p["barcode"], {})
            conn.execute(
                """INSERT INTO products
                   (barcode,product_name,brand,ingredients,category,
                    is_vegetarian,is_vegan,per_100g_sugar,per_100g_sodium,
                    per_100g_energy_kj,per_100g_sat_fat,per_100g_fiber,
                    per_100g_protein,fruits_veg_percent,image_url)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (p["barcode"], p["product_name"], p["brand"], p["ingredients"],
                 p["category"], p["is_vegetarian"], p["is_vegan"],
                 p["per_100g_sugar"], p["per_100g_sodium"],
                 n.get("energy_kj", 0), n.get("sat_fat", 0), n.get("fiber", 0),
                 n.get("protein", 0), n.get("fruits_veg", 0), p["image_url"]),
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
    "non_veg_ingredients": [
        "chicken", "beef", "pork", "mutton", "lamb", "turkey",
        "fish", "salmon", "tuna", "shrimp", "prawn", "anchovy", "sardine",
        "crab", "lobster", "squid", "clam", "oyster", "gelatin", "lard",
        "tallow", "suet", "rennet", "carmine", "isinglass", "bone broth",
        "meat extract", "poultry",
    ],
    "dairy_vegan": [
        "milk", "cream", "cheese", "butter", "whey", "casein",
        "lactose", "ghee", "paneer", "skim milk", "whole milk",
        "condensed milk", "dairy",
    ],
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
# Sensitivity Level — scales the caution/avoid thresholds ABOVE at
# comparison time only. It does not change the official nutrient data
# or create separate threshold tables, and it never applies to
# zero-tolerance checks (gluten/celiac, allergies) which always avoid.
#   low    (~1.3x) : warn later  — informational, fewer warnings
#   medium (1.0x)  : official thresholds — existing default behaviour
#   high   (~0.7x) : warn earlier — extra safety margin
# ─────────────────────────────────────────────
_SENSITIVITY_MULTIPLIER = {"low": 1.3, "medium": 1.0, "high": 0.7}
_SENSITIVITY_LABEL      = {"low": "Low", "medium": "Medium", "high": "High"}


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

    sensitivity = (profile.get("sensitivity") or "medium").lower()
    if sensitivity not in _SENSITIVITY_MULTIPLIER:
        sensitivity = "medium"
    sens_mult  = _SENSITIVITY_MULTIPLIER[sensitivity]
    sens_label = _SENSITIVITY_LABEL[sensitivity]

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

    # ── 6. Sugar — quantity-based (g / 100 g), scaled by sensitivity ────────
    is_diabetic     = has_d("diabetes")
    base_sugar      = _SUGAR["diabetes"] if is_diabetic else _SUGAR["default"]
    condition_label = "diabetes" if is_diabetic else "general"
    sugar_caution   = base_sugar["caution"] * sens_mult
    sugar_avoid     = base_sugar["avoid"] * sens_mult

    if sugar_g >= sugar_avoid:
        levels.append(2)
        if sensitivity == "medium":
            reasons.append(
                f"🚫 Very high sugar ({sugar_g:.1f} g/100 g) — exceeds {condition_label} avoid threshold "
                f"({sugar_avoid:.1f} g/100 g)"
            )
        else:
            reasons.append(
                f"🚫 Very high sugar ({sugar_g:.1f} g/100 g) — exceeds your {sens_label}-sensitivity avoid "
                f"limit of {sugar_avoid:.1f} g/100 g (official {condition_label} limit: {base_sugar['avoid']:.0f} g/100 g)"
            )
    elif sugar_g >= sugar_caution:
        levels.append(1)
        if sensitivity == "medium":
            reasons.append(
                f"⚠️ Elevated sugar ({sugar_g:.1f} g/100 g) — above {condition_label} caution threshold "
                f"({sugar_caution:.1f} g/100 g)"
            )
        else:
            reasons.append(
                f"⚠️ Elevated sugar ({sugar_g:.1f} g/100 g) — above your {sens_label}-sensitivity caution "
                f"limit of {sugar_caution:.1f} g/100 g (official {condition_label} limit: {base_sugar['caution']:.0f} g/100 g)"
            )
    elif sensitivity == "low" and sugar_g >= base_sugar["caution"]:
        # Low sensitivity: under the relaxed limit but at/above the official limit —
        # neutral awareness note only. Does not change the rating.
        reasons.append(
            f"ℹ️ Contains {sugar_g:.1f} g sugar/100 g — official {condition_label} caution limit is "
            f"{base_sugar['caution']:.0f} g/100 g. Your Low sensitivity setting keeps this informational."
        )

    # ── 7. Sodium — quantity-based (mg / 100 g), scaled by sensitivity ──────
    is_hypertensive = has_d("bp", "blood pressure", "hypertension")
    has_kidney      = has_d("kidney")
    if is_hypertensive or has_kidney:
        base_sodium  = _SODIUM["kidney"] if has_kidney else _SODIUM["hypertension"]
        sodium_label = "kidney disease" if has_kidney else "hypertension"
    else:
        base_sodium  = _SODIUM["default"]
        sodium_label = "general"
    sodium_caution = base_sodium["caution"] * sens_mult
    sodium_avoid   = base_sodium["avoid"] * sens_mult

    if sodium_mg >= sodium_avoid:
        levels.append(2)
        if sensitivity == "medium":
            reasons.append(
                f"🚫 Very high sodium ({sodium_mg:.0f} mg/100 g) — exceeds {sodium_label} avoid threshold "
                f"({sodium_avoid:.0f} mg/100 g)"
            )
        else:
            reasons.append(
                f"🚫 Very high sodium ({sodium_mg:.0f} mg/100 g) — exceeds your {sens_label}-sensitivity avoid "
                f"limit of {sodium_avoid:.0f} mg/100 g (official {sodium_label} limit: {base_sodium['avoid']:.0f} mg/100 g)"
            )
    elif sodium_mg >= sodium_caution:
        levels.append(1)
        if sensitivity == "medium":
            reasons.append(
                f"⚠️ High sodium ({sodium_mg:.0f} mg/100 g) — above {sodium_label} caution threshold "
                f"({sodium_caution:.0f} mg/100 g)"
            )
        else:
            reasons.append(
                f"⚠️ High sodium ({sodium_mg:.0f} mg/100 g) — above your {sens_label}-sensitivity caution "
                f"limit of {sodium_caution:.0f} mg/100 g (official {sodium_label} limit: {base_sodium['caution']:.0f} mg/100 g)"
            )
    elif sensitivity == "low" and sodium_mg >= base_sodium["caution"]:
        reasons.append(
            f"ℹ️ Contains {sodium_mg:.0f} mg sodium/100 g — official {sodium_label} caution limit is "
            f"{base_sodium['caution']:.0f} mg/100 g. Your Low sensitivity setting keeps this informational."
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
    if diet in ("vegetarian", "vegan"):
        non_veg_hits = [kw for kw in _ING["non_veg_ingredients"] if kw in text]
        if _has(text, "egg"):
            non_veg_hits.append("egg")
        if non_veg_hits:
            found_str = " / ".join(sorted(set(non_veg_hits))[:3])
            levels.append(1)
            reasons.append(
                f"⚠️ This product contains {found_str} — not suitable for your {diet} diet preference"
            )

    if diet == "vegan":
        dairy_hits = [kw for kw in _ING["dairy_vegan"] if kw in text]
        if dairy_hits:
            found_str = " / ".join(sorted(set(dairy_hits))[:3])
            levels.append(1)
            reasons.append(
                f"⚠️ This product contains {found_str} (dairy) — not suitable for your vegan diet preference"
            )

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
        info_notes  = [r for r in reasons if r.startswith("ℹ️")]
        reasons     = [
            "✅ All nutrient levels within safe thresholds for your health profile",
            "No allergens, zero-tolerance ingredients, or excessive sugar / sodium detected",
        ] + info_notes

    return rating, confidence, proba, reasons


# ─────────────────────────────────────────────
# Nutri-Score (universal nutritional quality per 100 g)
# Independent of the personalized Safe/Caution/Avoid engine above.
# Official European A–E front-of-pack grading (simplified point tables).
# ─────────────────────────────────────────────
_BEVERAGE_KEYWORDS = ["beverage", "drink", "juice", "soda", "cola", "water",
                      "tea", "coffee", "milk"]


def _ns_num(value):
    """Coerce a nutrient value to float; missing/None/blank/bad → 0.0."""
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _ns_points(value, bounds):
    """Return the index of the first bound `value` is <= to; else len(bounds)."""
    for i, b in enumerate(bounds):
        if value <= b:
            return i
    return len(bounds)


def _ns_fruits_points(pct):
    if pct <= 40:
        return 0
    if pct <= 60:
        return 2
    if pct <= 80:
        return 4
    return 5


def calculate_nutri_score(product_data):
    """
    Compute the Nutri-Score (A–E) for a product per 100 g / 100 ml.

    Accepts either a flat product dict (local DB shape with per_100g_* fields)
    or an Open Food Facts style dict containing a ``nutriments`` sub-dict.
    Missing/None values are treated as 0 and never raise.
    """
    product_data = product_data or {}
    nutriments = product_data.get("nutriments") or {}

    def _present(off_keys, flat_keys):
        for k in off_keys:
            if k in nutriments and nutriments[k] not in (None, ""):
                return True
        for k in flat_keys:
            if k in product_data and product_data[k] not in (None, ""):
                return True
        return False

    def _value(off_keys, flat_keys):
        for k in off_keys:
            if k in nutriments and nutriments[k] not in (None, ""):
                return _ns_num(nutriments[k])
        for k in flat_keys:
            if k in product_data and product_data[k] not in (None, ""):
                return _ns_num(product_data[k])
        return 0.0

    # ── Step 1: extract nutrients (with completeness tracking) ──────────────
    present_flags = []

    # Energy (kJ) — prefer kJ, else convert kcal ×4.184
    if _present(["energy-kj_100g", "energy_100g"], ["per_100g_energy_kj"]):
        energy_kj = _value(["energy-kj_100g", "energy_100g"], ["per_100g_energy_kj"])
        energy_present = True
    elif _present(["energy-kcal_100g"], ["per_100g_energy_kcal"]):
        energy_kj = _value(["energy-kcal_100g"], ["per_100g_energy_kcal"]) * 4.184
        energy_present = True
    else:
        energy_kj, energy_present = 0.0, False
    present_flags.append(energy_present)

    sugars = _value(["sugars_100g"], ["per_100g_sugar"])
    present_flags.append(_present(["sugars_100g"], ["per_100g_sugar"]))

    sat_fat = _value(["saturated-fat_100g"], ["per_100g_sat_fat"])
    present_flags.append(_present(["saturated-fat_100g"], ["per_100g_sat_fat"]))

    # Sodium (mg) — OFF sodium_100g is in g (×1000); salt_100g in g (×400);
    # flat per_100g_sodium is already in mg.
    if _present(["sodium_100g"], []):
        sodium_mg = _value(["sodium_100g"], []) * 1000
        sodium_present = True
    elif _present(["salt_100g"], []):
        sodium_mg = _value(["salt_100g"], []) * 400
        sodium_present = True
    elif _present([], ["per_100g_sodium"]):
        sodium_mg = _value([], ["per_100g_sodium"])
        sodium_present = True
    else:
        sodium_mg, sodium_present = 0.0, False
    present_flags.append(sodium_present)

    fiber = _value(["fiber_100g"], ["per_100g_fiber"])
    present_flags.append(_present(["fiber_100g"], ["per_100g_fiber"]))

    proteins = _value(["proteins_100g"], ["per_100g_protein"])
    present_flags.append(_present(["proteins_100g"], ["per_100g_protein"]))

    fruits_veg = _value(
        ["fruits-vegetables-nuts-estimate-from-ingredients_100g"],
        ["fruits_veg_percent"],
    )
    present_flags.append(_present(
        ["fruits-vegetables-nuts-estimate-from-ingredients_100g"],
        ["fruits_veg_percent"],
    ))

    # ── Step 2: negative points (0–10 each, max 40) ─────────────────────────
    energy_points = _ns_points(energy_kj, [335, 670, 1005, 1340, 1675,
                                           2010, 2345, 2680, 3015, 3350])
    sugars_points = _ns_points(sugars, [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45])
    sat_fat_points = _ns_points(sat_fat, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    sodium_points = _ns_points(sodium_mg, [90, 180, 270, 360, 450,
                                           540, 630, 720, 810, 900])
    negative_points = energy_points + sugars_points + sat_fat_points + sodium_points

    # ── Step 3: positive points (max 15) ────────────────────────────────────
    fiber_points = _ns_points(fiber, [0.9, 1.9, 2.8, 3.7, 4.7])
    protein_points = _ns_points(proteins, [1.6, 3.2, 4.8, 6.4, 8.0])
    fruits_veg_points = _ns_fruits_points(fruits_veg)

    # Official rule: if negatives are high and fruit/veg isn't maxed,
    # protein points are NOT counted toward the positive score.
    count_protein = not (negative_points >= 11 and fruits_veg_points < 5)
    positive_points = fiber_points + fruits_veg_points + (protein_points if count_protein else 0)

    # ── Step 4: final score & grade ─────────────────────────────────────────
    final_score = negative_points - positive_points

    category_str = (product_data.get("categories")
                    or product_data.get("category") or "").lower()
    name_str = (product_data.get("product_name")
                or product_data.get("name") or "").lower()
    haystack = f"{category_str} {name_str}"
    # Whole-word match (allowing simple plurals) so e.g. "cola" does NOT match
    # inside "chocolate" and "drink" still matches "drinks"/"juices".
    def _kw_present(kw):
        return re.search(r"\b" + re.escape(kw) + r"s?\b", haystack) is not None
    is_beverage = any(_kw_present(kw) for kw in _BEVERAGE_KEYWORDS)
    is_water = _kw_present("water")

    if is_beverage:
        if is_water:
            grade = "A"
        elif final_score <= 1:
            grade = "B"
        elif final_score <= 5:
            grade = "C"
        elif final_score <= 9:
            grade = "D"
        else:
            grade = "E"
    else:
        if final_score <= -1:
            grade = "A"
        elif final_score <= 2:
            grade = "B"
        elif final_score <= 10:
            grade = "C"
        elif final_score <= 18:
            grade = "D"
        else:
            grade = "E"

    # ── Step 5: data completeness & return ──────────────────────────────────
    missing = present_flags.count(False)
    if missing == 0:
        data_completeness = "full"
    elif missing <= 3:
        data_completeness = "partial"
    else:
        data_completeness = "minimal"

    insufficient_data = False
    if data_completeness == "minimal":
        grade = "B"
        insufficient_data = True

    return {
        "grade": grade,
        "score": final_score,
        "negative_points": negative_points,
        "positive_points": positive_points,
        "breakdown": {
            "energy_points": energy_points,
            "sugars_points": sugars_points,
            "saturated_fat_points": sat_fat_points,
            "sodium_points": sodium_points,
            "fiber_points": fiber_points,
            "protein_points": protein_points,
            "fruits_veg_points": fruits_veg_points,
        },
        "is_beverage": is_beverage,
        "data_completeness": data_completeness,
        "insufficient_data": insufficient_data,
    }


# ─────────────────────────────────────────────
# OpenFoodFacts fallback
# ─────────────────────────────────────────────
def fetch_from_openfoodfacts(barcode: str) -> dict | None:
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        print(f"[OFF] Fetching barcode {barcode} from Open Food Facts")
        resp = requests.get(url, timeout=10, headers={"User-Agent": "EatWiseAI/1.0"})
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != 1:
            print(f"[OFF] Barcode {barcode} not found in Open Food Facts (status={data.get('status')})")
            return None
        p = data["product"]
        nutriments = p.get("nutriments", {})

        # Energy in kJ: prefer energy-kj / energy, else convert from kcal
        energy_kj = nutriments.get("energy-kj_100g")
        if energy_kj in (None, ""):
            energy_kj = nutriments.get("energy_100g")
        if energy_kj in (None, ""):
            kcal = nutriments.get("energy-kcal_100g")
            energy_kj = float(kcal) * 4.184 if kcal not in (None, "") else 0

        # Sodium in mg: prefer sodium (g→mg), else salt (g→mg via ×400)
        if nutriments.get("sodium_100g") not in (None, ""):
            sodium_mg = float(nutriments["sodium_100g"]) * 1000
        elif nutriments.get("salt_100g") not in (None, ""):
            sodium_mg = float(nutriments["salt_100g"]) * 400
        else:
            sodium_mg = 0.0

        result = {
            "barcode": barcode,
            "product_name": p.get("product_name") or p.get("product_name_en") or "Unknown Product",
            "brand": p.get("brands", "Unknown"),
            "ingredients": p.get("ingredients_text_en") or p.get("ingredients_text", ""),
            "category": p.get("categories", "").split(",")[0].strip() if p.get("categories") else "Other",
            "categories": p.get("categories", "") or "",
            "is_vegetarian": int("en:vegetarian" in p.get("labels_tags", [])),
            "is_vegan": int("en:vegan" in p.get("labels_tags", [])),
            "per_100g_sugar": float(nutriments.get("sugars_100g") or 0),
            "per_100g_sodium": sodium_mg,
            "per_100g_energy_kj": float(energy_kj or 0),
            "per_100g_sat_fat": float(nutriments.get("saturated-fat_100g") or 0),
            "per_100g_fiber": float(nutriments.get("fiber_100g") or 0),
            "per_100g_protein": float(nutriments.get("proteins_100g") or 0),
            "fruits_veg_percent": float(
                nutriments.get("fruits-vegetables-nuts-estimate-from-ingredients_100g") or 0
            ),
            "image_url": p.get("image_front_url") or p.get("image_url", ""),
        }
        print(f"[OFF] Found: {result['product_name']} ({result['brand']})")
        return result
    except requests.exceptions.Timeout:
        print(f"[OFF] Timeout fetching barcode {barcode}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[OFF] Network error fetching barcode {barcode}: {e}")
        return None
    except Exception as e:
        print(f"[OFF] Unexpected error fetching barcode {barcode}: {type(e).__name__}: {e}")
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

    sensitivity = (data.get("sensitivity") or "medium").lower()
    if sensitivity not in ("low", "medium", "high"):
        sensitivity = "medium"

    user_id = data.get("user_id")
    conn = get_db()
    if user_id:
        conn.execute(
            """UPDATE users SET name=?,age=?,gender=?,weight=?,diseases=?,allergies=?,diet_type=?,sensitivity=?
               WHERE id=?""",
            (name, data.get("age"), data.get("gender"), data.get("weight"),
             diseases, allergies, data.get("diet_type", "non-vegetarian"), sensitivity, user_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    else:
        cur = conn.execute(
            """INSERT INTO users (name,age,gender,weight,diseases,allergies,diet_type,sensitivity)
               VALUES (?,?,?,?,?,?,?,?)""",
            (name, data.get("age"), data.get("gender"), data.get("weight"),
             diseases, allergies, data.get("diet_type", "non-vegetarian"), sensitivity),
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
           (barcode,product_name,brand,ingredients,category,is_vegetarian,is_vegan,
            per_100g_sugar,per_100g_sodium,per_100g_energy_kj,per_100g_sat_fat,
            per_100g_fiber,per_100g_protein,fruits_veg_percent,image_url)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (product_data["barcode"], product_data["product_name"], product_data["brand"],
         product_data["ingredients"], product_data["category"], product_data["is_vegetarian"],
         product_data["is_vegan"], product_data["per_100g_sugar"], product_data["per_100g_sodium"],
         product_data.get("per_100g_energy_kj", 0), product_data.get("per_100g_sat_fat", 0),
         product_data.get("per_100g_fiber", 0), product_data.get("per_100g_protein", 0),
         product_data.get("fruits_veg_percent", 0), product_data["image_url"]),
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

    print(f"[analyze] user_id={user_id} barcode={barcode}")

    conn = get_db()
    user_row    = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    product_row = conn.execute("SELECT * FROM products WHERE barcode=?", (barcode,)).fetchone()
    conn.close()

    if not user_row:
        print(f"[analyze] User {user_id} not found — stale localStorage ID?")
        return jsonify({"error": "Profile not found. Please reset and create a new profile."}), 404

    product_data = row_to_dict(product_row) if product_row else None
    if not product_data:
        print(f"[analyze] Barcode {barcode} not in local DB, trying Open Food Facts...")
        product_data = fetch_from_openfoodfacts(barcode)
        if not product_data:
            print(f"[analyze] Product {barcode} not found anywhere")
            return jsonify({"error": f"Product not found for barcode {barcode}. Try scanning a different product or use Sample Products."}), 404
        print(f"[analyze] Fetched from OFF: {product_data['product_name']}")

    profile = row_to_dict(user_row)
    profile["diseases"]  = json.loads(profile["diseases"] or "[]")
    profile["allergies"] = json.loads(profile["allergies"] or "[]")

    rating, confidence, probabilities, reasons = rate_product(product_data, profile)
    nutri_score = calculate_nutri_score(product_data)

    return jsonify({
        "rating":        rating,
        "confidence":    confidence,
        "probabilities": {
            "safe":    round(probabilities[0], 3),
            "caution": round(probabilities[1], 3),
            "avoid":   round(probabilities[2], 3),
        },
        "reasons":     reasons,
        "product":     product_data,
        "user_name":   profile["name"],
        "ml_used":     False,
        "nutri_score": nutri_score,
    }), 200


# ─────────────────────────────────────────────
# Chatbot helpers (offline hybrid engine)
# ─────────────────────────────────────────────
def _load_profile(conn, user_id):
    """Fetch a user profile dict with parsed diseases/allergies, or None."""
    user_row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user_row:
        return None
    profile = row_to_dict(user_row)
    profile["diseases"]  = json.loads(profile["diseases"] or "[]")
    profile["allergies"] = json.loads(profile["allergies"] or "[]")
    return profile


def _resolve_product(conn, barcode):
    """Return a product dict for the given barcode (local DB, then OFF), or None."""
    if not barcode or barcode == "general":
        return None
    row = conn.execute("SELECT * FROM products WHERE barcode=?", (barcode,)).fetchone()
    if row:
        return row_to_dict(row)
    # Fall back to Open Food Facts (offline chatbot still works if this fails)
    try:
        return fetch_from_openfoodfacts(barcode)
    except Exception:
        return None


def _candidate_products(conn, product):
    """Same-category products used to suggest healthier alternatives."""
    if not product:
        return []
    category = product.get("category")
    if not category:
        return []
    rows = conn.execute(
        "SELECT * FROM products WHERE category=? AND barcode!=?",
        (category, product.get("barcode", "")),
    ).fetchall()
    return [row_to_dict(r) for r in rows]


@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    message = (data.get("message") or "").strip()
    # Accept both `barcode` (spec) and `product_barcode` (existing frontend)
    barcode = data.get("barcode") or data.get("product_barcode")

    if not user_id:
        return jsonify({"reply": "Please set up your profile first to use the chatbot.",
                        "response": "Please set up your profile first to use the chatbot."}), 400
    if not message:
        return jsonify({"reply": "Please type a question and I'll help.",
                        "response": "Please type a question and I'll help."}), 400

    conn = get_db()
    try:
        profile = _load_profile(conn, user_id)
        if not profile:
            return jsonify({"reply": "Profile not found. Please create your profile first.",
                            "response": "Profile not found. Please create your profile first."}), 404

        product = _resolve_product(conn, barcode)
        rating_result = rate_product(product, profile) if product else None
        candidates = _candidate_products(conn, product)
        history = chat_memory.load_history(conn, user_id, barcode)

        # Persist the user's message, then generate + persist the reply
        chat_memory.save_message(conn, user_id, barcode, "user", message)

        result = chat_engine.generate_reply(
            message=message,
            profile=profile,
            product=product,
            rating_result=rating_result,
            history=history,
            candidates=candidates,
            rate_fn=rate_product,
        )

        chat_memory.save_message(
            conn, user_id, barcode, "bot", result["reply"],
            intent=result.get("intent"), rating=result.get("rating"),
        )
    finally:
        conn.close()

    return jsonify({
        "reply":     result["reply"],
        "response":  result["reply"],          # backward-compatible key
        "intent":    result.get("intent"),
        "rating":    result.get("rating"),
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


@app.route("/api/chat/history", methods=["GET"])
def chat_history():
    """Return persisted chat history for (user_id, barcode)."""
    user_id = request.args.get("user_id", type=int)
    barcode = request.args.get("barcode")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    conn = get_db()
    try:
        history = chat_memory.load_history(conn, user_id, barcode, limit=200)
    finally:
        conn.close()
    # Map to the frontend ChatMessage shape
    messages = [
        {"id": h["id"], "role": h["role"], "content": h["content"], "timestamp": h["timestamp"]}
        for h in history
    ]
    return jsonify({"messages": messages}), 200


@app.route("/api/chat/clear", methods=["POST", "DELETE"])
def chat_clear():
    """Clear the conversation for (user_id, barcode)."""
    data    = request.get_json(silent=True) or {}
    user_id = data.get("user_id") or request.args.get("user_id", type=int)
    barcode = data.get("barcode") or request.args.get("barcode")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    conn = get_db()
    try:
        removed = chat_memory.clear_history(conn, user_id, barcode)
    finally:
        conn.close()
    return jsonify({"cleared": removed}), 200


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
