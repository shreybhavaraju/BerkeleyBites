-- BerkeleyBites pgvector Migration
-- Adds vector embeddings for semantic dish search
-- Uses 384 dimensions for all-MiniLM-L6-v2 model (fast, good quality)

-- ===========================================
-- Enable pgvector Extension
-- ===========================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ===========================================
-- Add Embedding Columns to Dishes
-- ===========================================

-- Embedding column for semantic search (384 dims for all-MiniLM-L6-v2)
ALTER TABLE dishes
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Text used to generate the embedding (for debugging/regeneration)
ALTER TABLE dishes
ADD COLUMN IF NOT EXISTS embedding_text TEXT;

-- ===========================================
-- HNSW Index for Fast Approximate Nearest Neighbor Search
-- m=16: Number of bi-directional links (higher = better recall, more memory)
-- ef_construction=64: Size of dynamic candidate list during construction
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_dishes_embedding_hnsw
ON dishes USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ===========================================
-- Vector Search Function
-- Searches within a subset of dishes (pre-filtered by dietary restrictions)
-- Returns dishes ranked by cosine similarity
-- ===========================================
CREATE OR REPLACE FUNCTION search_dishes_by_embedding(
    query_embedding vector(384),
    dish_ids integer[],
    match_count integer DEFAULT 30
)
RETURNS TABLE (
    dish_id integer,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS dish_id,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM dishes d
    WHERE d.id = ANY(dish_ids)
      AND d.embedding IS NOT NULL
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ===========================================
-- Batch Update Embeddings Function
-- Efficiently updates embeddings for multiple dishes
-- ===========================================
CREATE OR REPLACE FUNCTION batch_update_embeddings(
    updates jsonb
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    update_count integer := 0;
    item jsonb;
BEGIN
    FOR item IN SELECT * FROM jsonb_array_elements(updates)
    LOOP
        UPDATE dishes
        SET
            embedding = (item->>'embedding')::vector(384),
            embedding_text = item->>'embedding_text'
        WHERE id = (item->>'dish_id')::integer;

        IF FOUND THEN
            update_count := update_count + 1;
        END IF;
    END LOOP;

    RETURN update_count;
END;
$$;

-- ===========================================
-- Get Dishes Without Embeddings
-- Useful for batch processing new dishes
-- ===========================================
CREATE OR REPLACE FUNCTION get_dishes_without_embeddings(
    target_date date DEFAULT CURRENT_DATE,
    batch_limit integer DEFAULT 100
)
RETURNS TABLE (
    dish_id integer,
    dish_name varchar(255),
    category varchar(100),
    dining_hall varchar(100),
    meal_period varchar(100),
    is_vegan boolean,
    is_vegetarian boolean,
    is_halal boolean,
    is_kosher boolean
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS dish_id,
        d.dish_name,
        d.category,
        d.dining_hall,
        d.meal_period,
        d.is_vegan,
        d.is_vegetarian,
        d.is_halal,
        d.is_kosher
    FROM dishes d
    WHERE d.scrape_date = target_date
      AND d.embedding IS NULL
    LIMIT batch_limit;
END;
$$;

-- ===========================================
-- Comments for Documentation
-- ===========================================
COMMENT ON COLUMN dishes.embedding IS 'Vector embedding (384 dims) for semantic search using all-MiniLM-L6-v2';
COMMENT ON COLUMN dishes.embedding_text IS 'Synthetic text used to generate the embedding';
COMMENT ON FUNCTION search_dishes_by_embedding IS 'Semantic search within filtered dish subset';
COMMENT ON FUNCTION batch_update_embeddings IS 'Batch update embeddings from JSONB array';
COMMENT ON FUNCTION get_dishes_without_embeddings IS 'Get dishes needing embedding generation';
