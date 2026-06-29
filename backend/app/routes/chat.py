"""AI chatbot routes — streaming and history."""
from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from app import db, limiter
from app.models.conversation import Conversation, Message
from app.models.profile import UserProfile
from app.models.product import Product
from app.services.chatbot import ChatbotService

chat_bp = Blueprint("chat", __name__)
chatbot = ChatbotService()


class ChatSchema(Schema):
    message = fields.Str(required=True)
    conversation_id = fields.Int(load_default=None)
    barcode = fields.Str(load_default=None)


@chat_bp.post("/chat")
@jwt_required()
@limiter.limit("30 per minute")
def chat():
    """Send a message and receive a streamed AI response."""
    schema = ChatSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 422

    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    product = None
    if data.get("barcode"):
        product = Product.query.filter_by(barcode=data["barcode"]).first()

    # Get or create conversation
    conv_id = data.get("conversation_id")
    if conv_id:
        conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
    else:
        conversation = Conversation(
            user_id=user_id,
            title=data["message"][:60],
            product_barcode=data.get("barcode"),
        )
        db.session.add(conversation)
        db.session.flush()

    # Persist user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=data["message"],
    )
    db.session.add(user_msg)
    db.session.commit()

    history = [
        {"role": m.role, "content": m.content}
        for m in conversation.messages[:-1]  # exclude the just-added user msg
    ]

    def generate():
        full_response = ""
        for chunk in chatbot.stream_response(
            user_message=data["message"],
            history=history,
            profile=profile,
            product=product,
        ):
            full_response += chunk
            yield chunk

        # Persist assistant message after stream completes
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
        )
        db.session.add(assistant_msg)
        db.session.commit()

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain",
        headers={
            "X-Conversation-Id": str(conversation.id),
            "Cache-Control": "no-cache",
        },
    )


@chat_bp.get("/history")
@jwt_required()
def get_history():
    """Return all conversations for the current user."""
    user_id = int(get_jwt_identity())
    conversations = (
        Conversation.query.filter_by(user_id=user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in conversations]), 200


@chat_bp.get("/history/<int:conv_id>")
@jwt_required()
def get_conversation(conv_id: int):
    """Return all messages in a specific conversation."""
    user_id = int(get_jwt_identity())
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404
    return jsonify({
        "conversation": conversation.to_dict(),
        "messages": [m.to_dict() for m in conversation.messages],
    }), 200


@chat_bp.delete("/history/<int:conv_id>")
@jwt_required()
def delete_conversation(conv_id: int):
    """Delete a conversation and all its messages."""
    user_id = int(get_jwt_identity())
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404
    db.session.delete(conversation)
    db.session.commit()
    return jsonify({"message": "Conversation deleted"}), 200


@chat_bp.delete("/history")
@jwt_required()
def delete_all_history():
    """Delete all conversations for the current user."""
    user_id = int(get_jwt_identity())
    Conversation.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "All history deleted"}), 200
