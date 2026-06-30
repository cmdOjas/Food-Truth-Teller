#!/usr/bin/env python3
"""
Simple ML training for Food Truth Teller.
Trains a Random Forest on (ingredient_features + user_health_features) → safe/caution/avoid.
Run: python train_simple.py
"""
import os
import json
import random
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

random.seed(42)
np.random.seed(42)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURE_NAMES = [
    # Ingredient features (0-13)
    "has_high_sugar",
    "has_high_sodium",
    "has_gluten",
    "has_dairy",
    "has_nuts",
    "has_preservatives",
    "has_artificial_colors",
    "has_trans_fat",
    "has_soy",
    "has_eggs",
    "has_artificial_sweeteners",
    "has_msg",
    "has_caffeine",
    "has_animal_ingredients",
    # User health features (14-24)
    "user_diabetes",
    "user_bp",
    "user_celiac",
    "user_lactose",
    "user_heart",
    "user_kidney",
    "user_nut_allergy",
    "user_gluten_allergy",
    "user_dairy_allergy",
    "user_egg_allergy",
    "user_soy_allergy",
]


def compute_label(f: list) -> int:
    """Rule-based labeling for synthetic training data. 0=safe, 1=caution, 2=avoid."""
    # Allergy direct hits → avoid
    if f[4] and f[20]: return 2   # nuts + nut_allergy
    if f[2] and (f[16] or f[21]): return 2  # gluten + celiac/gluten_allergy
    if f[3] and (f[17] or f[22]): return 2  # dairy + lactose/dairy_allergy
    if f[9] and f[23]: return 2   # eggs + egg_allergy
    if f[8] and f[24]: return 2   # soy + soy_allergy
    # Health condition + ingredient → avoid
    if f[0] and f[14]: return 2   # high_sugar + diabetes
    if f[1] and f[15]: return 2   # high_sodium + bp
    if f[1] and f[19]: return 2   # high_sodium + kidney
    if f[7] and f[18]: return 2   # trans_fat + heart
    if f[12] and f[18]: return 2  # caffeine + heart

    # Ingredient-level caution
    caution = 0
    if f[5]: caution += 1   # preservatives
    if f[6]: caution += 1   # artificial colors
    if f[7]: caution += 1   # trans fat (without heart condition)
    if f[0] and not f[14]: caution += 1  # high sugar (no diabetes)
    if f[1] and not f[15] and not f[19]: caution += 1  # high sodium
    if f[11]: caution += 0.5  # msg
    if f[10]: caution += 0.5  # artificial sweeteners
    if f[12]: caution += 0.5  # caffeine

    if caution >= 1: return 1
    return 0


def generate_training_data() -> tuple:
    samples = []

    def rnd_other(exclude, k):
        pool = [i for i in range(14) if i not in exclude]
        for i in random.sample(pool, min(k, len(pool))):
            yield i

    # --- SAFE samples ---
    # Wholesome products, healthy users
    for _ in range(35):
        f = [0] * 25
        samples.append((f[:], 0))

    for _ in range(15):
        f = [0] * 25
        f[8] = 1   # soy but no soy allergy
        f[3] = random.randint(0, 1)  # dairy but no dairy allergy
        samples.append((f[:], 0))

    # Low-caffeine, no conditions
    for _ in range(10):
        f = [0] * 25
        f[12] = 1
        samples.append((f[:], 0))  # caffeine alone is just minor caution → safe here for variety

    # --- CAUTION samples ---
    for _ in range(20):
        f = [0] * 25
        f[5] = 1   # preservatives
        for i in rnd_other([5], random.randint(0, 2)):
            f[i] = 1
        samples.append((f[:], 1))

    for _ in range(20):
        f = [0] * 25
        f[6] = 1   # artificial colors
        for i in rnd_other([6], random.randint(0, 2)):
            f[i] = 1
        samples.append((f[:], 1))

    for _ in range(15):
        f = [0] * 25
        f[0] = 1   # high sugar, no diabetes
        samples.append((f[:], 1))

    for _ in range(15):
        f = [0] * 25
        f[7] = 1   # trans fat, no heart
        samples.append((f[:], 1))

    for _ in range(15):
        f = [0] * 25
        f[1] = 1   # high sodium, no bp/kidney
        samples.append((f[:], 1))

    for _ in range(10):
        f = [0] * 25
        f[11] = 1  # msg
        f[5] = 1   # preservatives
        samples.append((f[:], 1))

    # --- AVOID samples ---
    for _ in range(25):
        f = [0] * 25
        f[0] = 1; f[14] = 1  # sugar + diabetes
        for i in rnd_other([0, 14], random.randint(0, 3)):
            f[i] = 1
        samples.append((f[:], 2))

    for _ in range(20):
        f = [0] * 25
        f[2] = 1; f[16] = 1  # gluten + celiac
        for i in rnd_other([2, 16], random.randint(0, 2)):
            f[i] = 1
        samples.append((f[:], 2))

    for _ in range(20):
        f = [0] * 25
        f[3] = 1; f[17] = 1  # dairy + lactose
        for i in rnd_other([3, 17], random.randint(0, 2)):
            f[i] = 1
        samples.append((f[:], 2))

    for _ in range(15):
        f = [0] * 25
        f[4] = 1; f[20] = 1  # nuts + nut allergy
        samples.append((f[:], 2))

    for _ in range(15):
        f = [0] * 25
        f[1] = 1; f[15] = 1  # sodium + bp
        for i in rnd_other([1, 15], random.randint(0, 2)):
            f[i] = 1
        samples.append((f[:], 2))

    for _ in range(10):
        f = [0] * 25
        f[7] = 1; f[18] = 1  # trans fat + heart
        samples.append((f[:], 2))

    for _ in range(10):
        f = [0] * 25
        f[9] = 1; f[23] = 1  # eggs + egg allergy
        samples.append((f[:], 2))

    for _ in range(10):
        f = [0] * 25
        f[8] = 1; f[24] = 1  # soy + soy allergy
        samples.append((f[:], 2))

    for _ in range(10):
        f = [0] * 25
        f[1] = 1; f[19] = 1  # sodium + kidney
        samples.append((f[:], 2))

    # Random mixed samples with rule-based labels for diversity
    for _ in range(30):
        f = [random.randint(0, 1) for _ in range(25)]
        label = compute_label(f)
        samples.append((f[:], label))

    random.shuffle(samples)
    X = [s[0] for s in samples]
    y = [s[1] for s in samples]
    return X, y


def main():
    X, y = generate_training_data()
    counts = {0: y.count(0), 1: y.count(1), 2: y.count(2)}
    print(f"Training data: {len(y)} samples — safe={counts[0]}, caution={counts[1]}, avoid={counts[2]}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest accuracy: {acc:.3f}")
    print(classification_report(y_test, y_pred, target_names=["safe", "caution", "avoid"]))

    model_path = os.path.join(MODELS_DIR, "health_model.pkl")
    features_path = os.path.join(MODELS_DIR, "feature_names.json")

    joblib.dump(clf, model_path)
    with open(features_path, "w") as fh:
        json.dump(FEATURE_NAMES, fh, indent=2)

    print(f"\nSaved model → {model_path}")
    print(f"Saved feature names → {features_path}")


if __name__ == "__main__":
    main()
