"""
NLP preprocessing pipeline for ingredient text.
Steps: lowercase → punctuation removal → tokenization → lemmatization → stopword removal → normalization
"""
from __future__ import annotations
import re
import string
from typing import List

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("punkt", quiet=True)
    _STOPWORDS = set(stopwords.words("english")) - {
        "no", "not", "nor", "without", "free"
    }
    _LEMMATIZER = WordNetLemmatizer()
    _NLTK_AVAILABLE = True
except ImportError:
    _NLTK_AVAILABLE = False
    _STOPWORDS = set()
    _LEMMATIZER = None

# E-number pattern (e.g. E102, E471b)
E_NUMBER_RE = re.compile(r"\be\d{3}[a-z]?\b", re.IGNORECASE)

# Additive synonym mapping (canonical form → keywords)
ADDITIVE_MAP: dict[str, str] = {
    "monosodium glutamate": "msg",
    "high fructose corn syrup": "hfcs",
    "hydrogenated": "trans_fat",
    "partially hydrogenated": "trans_fat",
    "sodium benzoate": "preservative_e211",
    "potassium sorbate": "preservative_e202",
    "tartrazine": "color_e102",
    "sunset yellow": "color_e110",
    "red 40": "color_red40",
    "yellow 5": "color_yellow5",
    "yellow 6": "color_yellow6",
    "aspartame": "sweetener_aspartame",
    "sucralose": "sweetener_sucralose",
    "acesulfame": "sweetener_acek",
    "bha": "antioxidant_bha",
    "bht": "antioxidant_bht",
    "tbhq": "antioxidant_tbhq",
}


class NLPProcessor:
    """Transforms raw ingredient text into a normalized token string."""

    def process(self, text: str) -> str:
        if not text:
            return ""

        text = text.lower()

        # Normalize additive synonyms before tokenization
        for phrase, normalized in ADDITIVE_MAP.items():
            text = text.replace(phrase, normalized)

        # Remove parentheses content but keep the tokens inside
        text = re.sub(r"[()]", " ", text)

        # Remove punctuation except hyphens (needed for e-numbers like e-102)
        text = text.translate(str.maketrans(string.punctuation.replace("-", ""), " " * (len(string.punctuation) - 1)))

        tokens = text.split()

        if _NLTK_AVAILABLE and _LEMMATIZER:
            tokens = [_LEMMATIZER.lemmatize(t) for t in tokens if t not in _STOPWORDS and len(t) > 1]
        else:
            tokens = [t for t in tokens if len(t) > 1]

        return " ".join(tokens)

    def extract_features(self, text: str) -> dict[str, int]:
        """Return a binary feature vector as a dict for direct model input."""
        processed = self.process(text)
        features = {
            "has_hfcs": int("hfcs" in processed),
            "has_trans_fat": int("trans_fat" in processed),
            "has_msg": int("msg" in processed),
            "has_artificial_color": int(any(c in processed for c in ["red40", "yellow5", "yellow6", "color_e"])),
            "has_preservative": int(any(p in processed for p in ["preservative_e", "sodium_benzoate", "benzoate", "sorbate"])),
            "has_sweetener": int(any(s in processed for s in ["sweetener_", "saccharin", "aspartame"])),
            "has_antioxidant": int(any(a in processed for a in ["bha", "bht", "tbhq"])),
            "has_hydrogenated": int("hydrogenat" in processed),
            "has_sugar": int("sugar" in processed or "sucrose" in processed or "glucose" in processed),
            "ingredient_count": len(processed.split()),
        }
        return features
