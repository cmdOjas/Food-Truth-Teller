"""Swagger/OpenAPI 3.0 JSON spec served at /api/swagger.json."""
from flask import Blueprint, jsonify

swagger_bp = Blueprint("swagger_spec", __name__)


@swagger_bp.get("/swagger.json")
def swagger_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Food Truth Teller API",
            "version": "1.0.0",
            "description": "AI-powered food product health analyzer chatbot backend.",
        },
        "servers": [{"url": "/api", "description": "API base"}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            }
        },
        "security": [{"BearerAuth": []}],
        "paths": {
            "/auth/register": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Register a new user",
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object", "required": ["email", "password", "name"], "properties": {"email": {"type": "string"}, "password": {"type": "string"}, "name": {"type": "string"}}}}}},
                    "responses": {"201": {"description": "Created"}, "409": {"description": "Email already exists"}},
                    "security": [],
                }
            },
            "/auth/login": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Login and receive JWT",
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object", "required": ["email", "password"], "properties": {"email": {"type": "string"}, "password": {"type": "string"}}}}}},
                    "responses": {"200": {"description": "JWT token"}, "401": {"description": "Invalid credentials"}},
                    "security": [],
                }
            },
            "/profile": {
                "get": {"tags": ["Profile"], "summary": "Get user health profile", "responses": {"200": {"description": "Profile data"}}},
                "post": {"tags": ["Profile"], "summary": "Create or update health profile", "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}}, "responses": {"200": {"description": "Saved"}}},
            },
            "/product/{barcode}": {
                "get": {
                    "tags": ["Product"],
                    "summary": "Look up product by barcode",
                    "parameters": [{"name": "barcode", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Product data"}, "404": {"description": "Not found"}},
                }
            },
            "/scan": {
                "post": {
                    "tags": ["Scan"],
                    "summary": "Scan a barcode",
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object", "required": ["barcode"], "properties": {"barcode": {"type": "string"}}}}}},
                    "responses": {"200": {"description": "Product data"}},
                }
            },
            "/analyze": {
                "post": {
                    "tags": ["Analysis"],
                    "summary": "Analyze product against user profile using ML",
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object", "required": ["barcode"], "properties": {"barcode": {"type": "string"}}}}}},
                    "responses": {"200": {"description": "Analysis result"}},
                }
            },
            "/chat": {
                "post": {
                    "tags": ["Chat"],
                    "summary": "Send a message to the AI chatbot",
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object", "required": ["message"], "properties": {"message": {"type": "string"}, "conversation_id": {"type": "integer"}, "barcode": {"type": "string"}}}}}},
                    "responses": {"200": {"description": "Streamed AI response"}},
                }
            },
            "/history": {
                "get": {"tags": ["Chat"], "summary": "Get all conversations", "responses": {"200": {"description": "List of conversations"}}},
                "delete": {"tags": ["Chat"], "summary": "Delete all conversation history", "responses": {"200": {"description": "Deleted"}}},
            },
            "/recommendations": {
                "get": {"tags": ["Product"], "summary": "Get healthy product recommendations", "responses": {"200": {"description": "List of products"}}}
            },
        },
    }
    return jsonify(spec)
