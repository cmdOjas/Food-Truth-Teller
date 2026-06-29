"""
Generates a labeled food product ingredient dataset for training.
Run: python generate_dataset.py

Outputs: food_health_dataset.csv
"""
import csv
import random
import os

SAFE_INGREDIENTS = [
    "water, whole grain oats, natural honey, blueberries, almonds",
    "organic apples, cinnamon, lemon juice",
    "brown rice, black beans, olive oil, garlic, cumin",
    "spinach, kale, cucumber, celery, ginger, lemon",
    "quinoa, chickpeas, parsley, olive oil, lemon",
    "oat flour, banana, eggs, vanilla extract, baking powder",
    "greek yogurt, strawberries, granola, honey",
    "lentils, carrots, tomatoes, onion, turmeric, water",
    "avocado, tomato, onion, cilantro, lime juice, salt",
    "sweet potato, olive oil, rosemary, sea salt",
    "whole wheat flour, water, yeast, salt",
    "almonds, cashews, walnuts, pumpkin seeds, raisins",
    "skim milk, oats, blueberries, flaxseed",
    "tofu, broccoli, soy sauce, garlic, ginger, sesame oil",
    "salmon, lemon, dill, olive oil, garlic",
    "chicken breast, brown rice, steamed broccoli, olive oil",
    "egg whites, spinach, mushrooms, onion, garlic",
    "plain oatmeal, chia seeds, almond milk, banana",
    "whole grain pasta, tomatoes, basil, olive oil, garlic",
    "orange, grapefruit, lemon, sparkling water",
    "coconut water, lime, mint",
    "barley, mushrooms, thyme, vegetable broth",
    "edamame, sea salt",
    "hummus, olive oil, lemon, garlic, chickpeas, tahini",
    "black bean soup, cumin, cayenne, lime",
    "turkey breast, lettuce, tomato, mustard, whole grain bread",
    "beet, carrot, apple, ginger, lemon juice",
    "tempeh, tamari, sesame oil, garlic, ginger",
    "chia seeds, almond milk, vanilla, maple syrup",
    "air popped popcorn, nutritional yeast, sea salt",
]

UNSAFE_INGREDIENTS = [
    "high fructose corn syrup, hydrogenated oil, artificial flavors, red 40, sodium benzoate",
    "sugar, palm oil, artificial colors, maltodextrin, monosodium glutamate",
    "white flour, sugar, partially hydrogenated soybean oil, artificial vanilla, bha bht",
    "corn syrup solids, trans fat, sucralose, acesulfame potassium, tartrazine",
    "modified starch, sodium nitrite, carmine, aspartame, potassium sorbate",
    "bleached flour, shortening, dextrose, artificial sweetener, e102 e110",
    "sugar, milk chocolate, palm kernel oil, soy lecithin, vanillin artificial flavor",
    "enriched flour, sugar, soybean oil, salt, tbhq, nonfat milk",
    "glucose syrup, cocoa butter, milk powder, emulsifiers e471 e472, vanillin",
    "hydrogenated cottonseed oil, high fructose corn syrup, artificial color blue 1",
    "sodium benzoate, potassium sorbate, acesulfame k, sucralose, red 40 lake",
    "sodium nitrite, sodium phosphate, corn syrup, dextrose, modified corn starch",
    "bleached wheat flour, sugar, leavening, soybean oil, artificial flavor, bha",
    "sugar, partially hydrogenated palm oil, whey, artificial color, propylene glycol",
    "corn syrup, glucose, gelatin, artificial flavors, yellow 5 yellow 6",
    "processed cheese, sodium phosphate, sorbic acid, artificial color, carmine",
    "sugar, maltitol, palm oil, cocoa powder, vanillin, e471 e476 lecithin",
    "modified potato starch, monosodium glutamate, artificial flavor, disodium inosinate",
    "high fructose corn syrup, caramel color, phosphoric acid, natural flavors",
    "enriched flour, sugar, corn syrup, soybean oil, salt, tbhq, artificial color",
    "sodium nitrate, dextrose, modified food starch, carrageenan, lactic acid starter",
    "hydrogenated vegetable oil, sugar, skim milk powder, sodium caseinate, e471",
    "glucose fructose syrup, acidity regulator e330, colorings e150d e160a, e211",
    "artificial sweeteners aspartame saccharin acesulfame, food dyes fd c red 3",
    "partially hydrogenated soybean oil, high fructose corn syrup, artificial vanilla",
    "monosodium glutamate, disodium guanylate, disodium inosinate, sodium diacetate",
    "sugar, palm fat, whey powder, skimmed milk powder, soy lecithin, pgpr vanillin",
    "sodium benzoate, potassium sorbate, citric acid, caramel color, phosphoric acid",
    "corn syrup solids, hydrogenated coconut oil, sodium caseinate, dipotassium phosphate",
    "butylated hydroxytoluene, butylated hydroxyanisole, propyl gallate, tbhq",
]

CAUTION_INGREDIENTS = [
    "whole wheat, milk, sugar, eggs, natural vanilla, butter",
    "oats, wheat, honey, raisins, sunflower oil, sea salt",
    "brown sugar, whole milk, eggs, vanilla, cocoa powder, butter",
    "salt, sunflower oil, whey, milk, natural flavoring",
    "pasteurized milk, cream, salt, cheese cultures, enzymes",
    "soy flour, glucose, salt, natural flavors, sunflower lecithin",
    "wheat flour, sugar, canola oil, salt, egg, milk",
    "whole grain wheat, malt syrup, salt, sugar, nonfat milk",
    "evaporated cane juice, whole wheat flour, cocoa, sea salt, vanilla",
    "milk, cream, sugar, eggs, vanilla bean",
]

rows = []

for ing in SAFE_INGREDIENTS:
    rows.append({"ingredients": ing, "label": 0, "prediction": "Safe"})

for ing in UNSAFE_INGREDIENTS:
    rows.append({"ingredients": ing, "label": 1, "prediction": "Avoid"})

for ing in CAUTION_INGREDIENTS:
    rows.append({"ingredients": ing, "label": 0, "prediction": "Caution"})

# Augment to 500 rows
random.seed(42)
while len(rows) < 500:
    if random.random() < 0.5:
        base = random.choice(UNSAFE_INGREDIENTS)
        extra = random.choice(["artificial color", "sodium benzoate", "high fructose corn syrup", "bht bha tbhq", "msg monosodium glutamate"])
        rows.append({"ingredients": base + ", " + extra, "label": 1, "prediction": "Avoid"})
    else:
        base = random.choice(SAFE_INGREDIENTS)
        extra = random.choice(["sea salt", "organic cane sugar", "lemon juice", "apple cider vinegar", "spices"])
        rows.append({"ingredients": base + ", " + extra, "label": 0, "prediction": "Safe"})

random.shuffle(rows)

out_path = os.path.join(os.path.dirname(__file__), "food_health_dataset.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ingredients", "label", "prediction"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} rows → {out_path}")
