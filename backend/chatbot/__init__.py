"""
Offline nutrition chatbot package.

A fully offline, rule + NLP based conversational engine — no LLM, no
external API, no API keys. It combines the user's health profile, product
data, ingredient knowledge base, the rule-engine rating, conversation
memory and intent detection to answer questions about a scanned product.

Public entry point: `chatbot.engine.generate_reply(...)`.
"""
from . import engine, intents, knowledge_base, memory  # noqa: F401

__all__ = ["engine", "intents", "knowledge_base", "memory"]
