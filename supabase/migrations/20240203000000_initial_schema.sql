-- BerkeleyBites Initial Schema
-- This migration creates all tables for the Supabase-backed BerkeleyBites app

-- ===========================================
-- Table: dishes
-- Stores menu items from UC Berkeley dining halls
-- ===========================================
CREATE TABLE dishes (
    id SERIAL PRIMARY KEY,
    dish_name VARCHAR(255) NOT NULL,
    dining_hall VARCHAR(100) NOT NULL,
    dining_hall_status VARCHAR(50) NOT NULL,
    meal_period VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    has_milk BOOLEAN DEFAULT FALSE,
    has_egg BOOLEAN DEFAULT FALSE,
    has_fish BOOLEAN DEFAULT FALSE,
    has_shellfish BOOLEAN DEFAULT FALSE,
    has_tree_nuts BOOLEAN DEFAULT FALSE,
    has_wheat BOOLEAN DEFAULT FALSE,
    has_peanuts BOOLEAN DEFAULT FALSE,
    has_soybeans BOOLEAN DEFAULT FALSE,
    has_sesame BOOLEAN DEFAULT FALSE,
    has_gluten BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_halal BOOLEAN DEFAULT FALSE,
    is_kosher BOOLEAN DEFAULT FALSE,
    has_pork BOOLEAN DEFAULT FALSE,
    has_alcohol BOOLEAN DEFAULT FALSE,
    scrape_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(dish_name, dining_hall, meal_period, scrape_date)
);

-- Indexes for efficient querying
CREATE INDEX idx_dishes_scrape_date ON dishes(scrape_date);
CREATE INDEX idx_dishes_dining_hall ON dishes(dining_hall);
CREATE INDEX idx_dishes_meal_period ON dishes(meal_period);

-- ===========================================
-- Table: user_profiles
-- Stores user dietary preferences and restrictions
-- ===========================================
CREATE TABLE user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_pescatarian BOOLEAN DEFAULT FALSE,
    is_halal BOOLEAN DEFAULT FALSE,
    is_kosher BOOLEAN DEFAULT FALSE,
    avoid_milk BOOLEAN DEFAULT FALSE,
    avoid_eggs BOOLEAN DEFAULT FALSE,
    avoid_gluten BOOLEAN DEFAULT FALSE,
    avoid_nuts BOOLEAN DEFAULT FALSE,
    avoid_soy BOOLEAN DEFAULT FALSE,
    prefer_low_carbon BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- Table: feedback
-- Stores user dish ratings (liked/disliked)
-- ===========================================
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    dish_id INTEGER REFERENCES dishes(id) ON DELETE CASCADE,
    dish_name VARCHAR(255) NOT NULL,
    liked BOOLEAN NOT NULL,
    rating_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, dish_id, rating_date)
);

-- Indexes for efficient querying
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_user_date ON feedback(user_id, rating_date);

-- ===========================================
-- Table: user_moods
-- Stores user mood for personalized recommendations
-- ===========================================
CREATE TABLE user_moods (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    mood VARCHAR(50) NOT NULL DEFAULT 'happy',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_mood CHECK (mood IN ('happy', 'grumpy', 'stressed', 'tired', 'adventurous'))
);

-- ===========================================
-- Trigger: Auto-update updated_at timestamp
-- ===========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_moods_updated_at
    BEFORE UPDATE ON user_moods
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
