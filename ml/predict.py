"""
Standalone ingredient safety predictor.
Usage: python predict.py "sugar, hydrogenated oil, red 40, sodium benzoate"
"""
from __future__ import annotations
import argparse
import os
import joblib
from nlp_processor import NLPProcessor

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def load_model():
    model_path = os.path.join(MODELS_DIR, "health_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run train.py first."
        )
    return joblib.load(model_path)


def predict(ingredients_text: str) -> dict:
    processor = NLPProcessor()
    processed = processor.process(ingredients_text)

    model = load_model()
    proba = model.predict_proba([processed])[0]
    predicted_class = model.predict([processed])[0]

    label = "Avoid" if predicted_class == 1 else "Safe"
    confidence = round(max(proba) * 100, 2)

    return {
        "input": ingredients_text,
        "processed": processed,
        "prediction": label,
        "confidence": confidence,
        "class_probabilities": {
            "safe": round(proba[0] * 100, 2),
            "avoid": round(proba[1] * 100, 2),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict ingredient safety")
    parser.add_argument("ingredients", nargs="?", default="sugar, hydrogenated oil, red 40, sodium benzoate")
    args = parser.parse_args()

    result = predict(args.ingredients)
    print(f"\nIngredients : {result['input']}")
    print(f"Processed   : {result['processed']}")
    print(f"Prediction  : {result['prediction']} ({result['confidence']}% confidence)")
    print(f"Probabilities: Safe={result['class_probabilities']['safe']}%, Avoid={result['class_probabilities']['avoid']}%")
