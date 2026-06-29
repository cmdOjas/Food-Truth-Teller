# API Reference

Base URL: `http://localhost:5000/api`  
Auth: All endpoints except `/auth/register` and `/auth/login` require `Authorization: Bearer <JWT>` header.

---

## Auth

### POST /auth/register
Register a new account.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "Jane Doe"
}
```
**Response 201:**
```json
{
  "message": "Account created",
  "token": "eyJ...",
  "user": { "id": 1, "email": "user@example.com", "name": "Jane Doe" }
}
```

### POST /auth/login
```json
{ "email": "user@example.com", "password": "securepassword" }
```
**Response 200:** `{ "token": "eyJ...", "user": {...} }`

---

## Profile

### POST /profile
```json
{
  "age": 35,
  "gender": "female",
  "weight_kg": 68.0,
  "height_cm": 168.0,
  "health_conditions": ["Diabetes", "Hypertension"],
  "allergies": ["gluten", "dairy"],
  "diet_preference": "vegetarian",
  "goals": ["Manage Diabetes", "Heart Health"]
}
```
**Response 200:** `{ "message": "Profile saved", "profile": {...} }`

### GET /profile
**Response 200:** Full profile object including computed BMI.

---

## Product

### GET /product/:barcode
Look up product by barcode. Fetches from Open Food Facts if not cached.

**Response 200:** Full product object.

### POST /scan
```json
{ "barcode": "737628064502" }
```
**Response 200:** `{ "product": {...}, "source": "local" | "openfoodfacts" }`

### POST /analyze
```json
{ "barcode": "737628064502" }
```
**Response 200:**
```json
{
  "prediction": "Avoid",
  "confidence": 94.5,
  "issues": [
    { "ingredient": "Sugar: 32g/100g", "reason": "Contains high_sugar_nutrition: risky for diabetes" }
  ],
  "all_flags": [...],
  "nutriscore": "e",
  "nova_group": 4,
  "is_vegetarian": false,
  "is_vegan": false
}
```

### GET /recommendations?category=snacks
Returns products with Nutriscore A or B.

---

## Chat

### POST /chat
Streams the AI response as plain text.

**Body:**
```json
{
  "message": "Can I eat this?",
  "conversation_id": null,
  "barcode": "737628064502"
}
```
**Response 200:** Streamed text/plain  
**Header:** `X-Conversation-Id: 42`

### GET /history
Returns list of all conversations.

### GET /history/:id
Returns conversation with all messages.

### DELETE /history/:id
Deletes a conversation.

### DELETE /history
Deletes all conversations for the current user.

---

## Error Responses

| Status | Meaning |
|---|---|
| 400 | Bad request |
| 401 | Unauthorized / invalid JWT |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Conflict (e.g. duplicate email) |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

Error format:
```json
{ "error": "Human-readable message", "details": { ... } }
```
