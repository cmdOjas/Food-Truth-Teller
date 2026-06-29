"""Chat conversation and message models."""
from datetime import datetime, timezone
from sqlalchemy import JSON
from app import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), default="New Conversation")
    product_barcode = db.Column(db.String(50), db.ForeignKey("products.barcode"), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", back_populates="conversations")
    messages = db.relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )
    product = db.relationship("Product", foreign_keys=[product_barcode], primaryjoin="Conversation.product_barcode == Product.barcode")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "product_barcode": self.product_barcode,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Conversation {self.id}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' | 'assistant' | 'system'
    content = db.Column(db.Text, nullable=False)
    extra_data = db.Column(JSON, default=dict)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    conversation = db.relationship("Conversation", back_populates="messages")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "metadata": self.extra_data or {},
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Message {self.id} role={self.role}>"
