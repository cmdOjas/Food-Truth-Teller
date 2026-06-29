-- Food Truth Teller — PostgreSQL Schema
-- Run: psql -U postgres -d food_truth_teller -f schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For ILIKE search optimization

-- ─────────────────────────────────────────
-- Users
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name          VARCHAR(150) NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- ─────────────────────────────────────────
-- User Health Profiles
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    age               SMALLINT CHECK (age > 0 AND age < 150),
    gender            VARCHAR(20),
    weight_kg         NUMERIC(5, 2),
    height_cm         NUMERIC(5, 2),
    bmi               NUMERIC(4, 2),
    health_conditions JSONB NOT NULL DEFAULT '[]',
    allergies         JSONB NOT NULL DEFAULT '[]',
    diet_preference   VARCHAR(50),
    goals             JSONB NOT NULL DEFAULT '[]',
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- Products
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id                  SERIAL PRIMARY KEY,
    barcode             VARCHAR(50) NOT NULL UNIQUE,
    name                VARCHAR(500) NOT NULL,
    brand               VARCHAR(255),
    category            VARCHAR(255),
    ingredients_text    TEXT,
    ingredients_parsed  JSONB NOT NULL DEFAULT '[]',
    nutrition_per_100g  JSONB NOT NULL DEFAULT '{}',
    image_url           VARCHAR(1000),
    is_vegetarian       BOOLEAN NOT NULL DEFAULT FALSE,
    is_vegan            BOOLEAN NOT NULL DEFAULT FALSE,
    nutriscore_grade    CHAR(1) CHECK (nutriscore_grade IN ('a','b','c','d','e')),
    nova_group          SMALLINT CHECK (nova_group BETWEEN 1 AND 4),
    allergens           JSONB NOT NULL DEFAULT '[]',
    additives           JSONB NOT NULL DEFAULT '[]',
    labels              JSONB NOT NULL DEFAULT '[]',
    source              VARCHAR(50) NOT NULL DEFAULT 'openfoodfacts',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_barcode   ON products (barcode);
CREATE INDEX IF NOT EXISTS idx_products_category  ON products USING gin (category gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_nutriscore ON products (nutriscore_grade);

-- ─────────────────────────────────────────
-- Conversations
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    product_barcode VARCHAR(50) REFERENCES products (barcode) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations (user_id);

-- ─────────────────────────────────────────
-- Messages
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id, created_at);

-- ─────────────────────────────────────────
-- Updated-at trigger (auto-update timestamp)
-- ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_profiles_updated
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
