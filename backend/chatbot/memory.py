"""
Conversation memory for the offline nutrition chatbot.

Chat turns are persisted in the SQLite `chat_messages` table so a
conversation survives page reloads and is scoped to a single product
(via barcode). The helpers here are pure functions that take an existing
sqlite3 connection — the engine and routes stay decoupled from DB setup.

A conversation "key" is (user_id, barcode). For general chat that is not
tied to a scanned product, the caller passes barcode = "general".
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

# How many recent turns to feed back into the engine as context
HISTORY_CONTEXT_LIMIT = 12


def normalize_barcode(barcode: Optional[str]) -> str:
    """Chat not tied to a product is stored under the 'general' bucket."""
    return (barcode or "general").strip() or "general"


def save_message(conn: sqlite3.Connection, user_id: int, barcode: Optional[str],
                 role: str, content: str, intent: Optional[str] = None,
                 rating: Optional[str] = None) -> None:
    """Persist a single chat turn. `role` is 'user' or 'bot'."""
    conn.execute(
        """INSERT INTO chat_messages (user_id, barcode, role, content, intent, rating, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (user_id, normalize_barcode(barcode), role, content, intent, rating,
         datetime.utcnow().isoformat()),
    )
    conn.commit()


def load_history(conn: sqlite3.Connection, user_id: int, barcode: Optional[str],
                 limit: int = HISTORY_CONTEXT_LIMIT) -> list[dict]:
    """
    Return the most recent turns for (user_id, barcode) in chronological order.
    Each item: {id, role, content, intent, rating, timestamp}.
    """
    rows = conn.execute(
        """SELECT id, role, content, intent, rating, created_at
           FROM chat_messages
           WHERE user_id=? AND barcode=?
           ORDER BY id DESC LIMIT ?""",
        (user_id, normalize_barcode(barcode), limit),
    ).fetchall()
    history = [
        {
            "id": str(r["id"]),
            "role": r["role"],
            "content": r["content"],
            "intent": r["intent"],
            "rating": r["rating"],
            "timestamp": r["created_at"],
        }
        for r in rows
    ]
    history.reverse()  # chronological
    return history


def clear_history(conn: sqlite3.Connection, user_id: int, barcode: Optional[str]) -> int:
    """Delete all turns for (user_id, barcode). Returns rows removed."""
    cur = conn.execute(
        "DELETE FROM chat_messages WHERE user_id=? AND barcode=?",
        (user_id, normalize_barcode(barcode)),
    )
    conn.commit()
    return cur.rowcount


def last_bot_context(history: list[dict]) -> tuple[Optional[str], Optional[str]]:
    """
    Return (last_intent, last_rating) from the most recent BOT turn, used to
    resolve follow-up questions such as a bare "why?".
    """
    for turn in reversed(history):
        if turn["role"] == "bot":
            return turn.get("intent"), turn.get("rating")
    return None, None
