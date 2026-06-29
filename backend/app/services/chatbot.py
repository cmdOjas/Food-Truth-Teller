"""
AI chatbot service using OpenAI GPT with full context injection:
user profile + product data + ML analysis result.
"""
from __future__ import annotations
import os
import json
from typing import Generator, Optional
from flask import current_app
import openai


SYSTEM_PROMPT = """You are a certified nutrition and health expert assistant integrated into a food product health analyzer app.
Your role is to help users understand whether a specific packaged food product is safe and healthy for them based on their personal health profile, medical conditions, allergies, dietary preferences, and the product's ingredients.

Guidelines:
- Always be empathetic, clear, and non-alarmist.
- Use simple, everyday language. Avoid jargon.
- Explain WHY an ingredient may be harmful for the user's specific condition.
- Always suggest healthier alternatives when recommending avoidance.
- Cite ingredient names from the product data when available.
- When uncertain, acknowledge it honestly.
- Format responses with clear sections when helpful (e.g., "⚠️ Concerns:", "✅ Safe for you:", "💡 Alternatives:").
- Remember the conversation history and refer back to it naturally."""


class ChatbotService:
    """Wraps OpenAI API for streaming chat completions with context injection."""

    def __init__(self) -> None:
        self._client: Optional[openai.OpenAI] = None

    def _get_client(self) -> openai.OpenAI:
        if self._client is None:
            api_key = current_app.config.get("OPENAI_API_KEY", "")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not configured")
            self._client = openai.OpenAI(api_key=api_key)
        return self._client

    def _build_context_message(self, profile, product) -> str:
        parts = []
        if profile:
            parts.append(f"""USER HEALTH PROFILE:
- Age: {profile.age}, Gender: {profile.gender}
- Weight: {profile.weight_kg} kg, Height: {profile.height_cm} cm, BMI: {profile.bmi}
- Health Conditions: {', '.join(profile.health_conditions or []) or 'None'}
- Allergies: {', '.join(profile.allergies or []) or 'None'}
- Diet Preference: {profile.diet_preference or 'No preference'}
- Goals: {', '.join(profile.goals or []) or 'None specified'}""")

        if product:
            nutrition = product.nutrition_per_100g or {}
            parts.append(f"""SCANNED PRODUCT:
- Name: {product.name}
- Brand: {product.brand or 'Unknown'}
- Category: {product.category or 'Unknown'}
- Ingredients: {product.ingredients_text or 'Not available'}
- Nutriscore: {(product.nutriscore_grade or 'N/A').upper()}
- NOVA Group: {product.nova_group or 'N/A'} (1=minimally processed, 4=ultra-processed)
- Is Vegan: {product.is_vegan}, Is Vegetarian: {product.is_vegetarian}
- Allergens: {', '.join(product.allergens or []) or 'None listed'}
- Additives: {', '.join(product.additives or []) or 'None listed'}
- Nutrition per 100g: Energy {nutrition.get('energy_kcal', 'N/A')} kcal, Sugars {nutrition.get('sugars_g', 'N/A')}g, Fat {nutrition.get('fat_g', 'N/A')}g, Saturated fat {nutrition.get('saturated_fat_g', 'N/A')}g, Sodium {nutrition.get('sodium_mg', 'N/A')}mg, Protein {nutrition.get('proteins_g', 'N/A')}g""")

            # Run ingredient analysis for additional context
            from app.services.analyzer import IngredientAnalyzer
            analyzer = IngredientAnalyzer()
            analysis = analyzer.analyze(product, profile)
            parts.append(f"""ML ANALYSIS RESULT:
- Prediction: {analysis['prediction']} (Confidence: {analysis['confidence']}%)
- Key Issues: {json.dumps(analysis['issues'], indent=2)}""")

        return "\n\n".join(parts)

    def stream_response(
        self,
        user_message: str,
        history: list[dict],
        profile=None,
        product=None,
    ) -> Generator[str, None, None]:
        """Stream OpenAI response chunks as a generator."""
        client = self._get_client()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Inject context as a system message if we have profile/product data
        context = self._build_context_message(profile, product)
        if context:
            messages.append({"role": "system", "content": f"Current context:\n{context}"})

        # Add conversation history (cap at last 20 messages to stay within token limits)
        messages.extend(history[-20:])
        messages.append({"role": "user", "content": user_message})

        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                temperature=0.4,
                max_tokens=1000,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except openai.AuthenticationError:
            yield "⚠️ AI service is not configured. Please set your OpenAI API key."
        except openai.RateLimitError:
            yield "⚠️ AI service is temporarily overloaded. Please try again shortly."
        except Exception as exc:
            current_app.logger.error("OpenAI error: %s", exc)
            yield "⚠️ An error occurred while generating a response. Please try again."
