-- AI Fashion Consultant Database Schema
-- SQLite compatible

-- Wardrobe Items Table
CREATE TABLE IF NOT EXISTS wardrobe_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garment_type TEXT NOT NULL,
    color TEXT NOT NULL,
    secondary_colors TEXT,  -- JSON array
    pattern TEXT,
    formality TEXT,
    season TEXT,  -- JSON array
    material TEXT,
    style_tags TEXT,  -- JSON array
    brand TEXT,
    condition TEXT,
    image_path TEXT,
    times_worn INTEGER DEFAULT 0,
    last_worn DATE,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags_json TEXT,  -- Full JSON of all tags
    CONSTRAINT check_formality CHECK (formality IN ('casual', 'business casual', 'formal', 'athletic', 'lounge')),
    CONSTRAINT check_condition CHECK (condition IN ('new', 'good', 'worn', 'damaged'))
);

-- Outfits Table
CREATE TABLE IF NOT EXISTS outfits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outfit_json TEXT NOT NULL,  -- Full outfit specification
    occasion TEXT,
    weather TEXT,
    temperature REAL,
    gender TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_feedback TEXT,
    rating INTEGER,  -- 1-5
    worn_date DATE,
    confidence_score REAL,
    CONSTRAINT check_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT check_occasion CHECK (occasion IN ('casual', 'work', 'wedding', 'party', 'formal', 'travel', 'date', 'festival'))
);

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT,
    favorite_colors TEXT,  -- JSON array
    disliked_colors TEXT,  -- JSON array
    preferred_styles TEXT,  -- JSON array
    avoided_patterns TEXT,  -- JSON array
    sizes TEXT,  -- JSON object
    preferences_json TEXT,  -- Full preferences
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_gender CHECK (gender IN ('male', 'female', 'unisex'))
);

-- Feedback History Table
CREATE TABLE IF NOT EXISTS feedback_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outfit_id INTEGER,
    feedback_type TEXT,  -- positive, negative, neutral
    feedback_text TEXT,
    sentiment_score REAL,  -- -1 to 1
    insights_json TEXT,  -- Extracted insights
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
    CONSTRAINT check_feedback_type CHECK (feedback_type IN ('positive', 'negative', 'neutral'))
);

-- Outfit Items Junction Table (Many-to-Many)
CREATE TABLE IF NOT EXISTS outfit_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outfit_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_role TEXT,  -- 'top', 'bottom', 'shoes', 'outerwear', 'accessory'
    FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES wardrobe_items(id) ON DELETE CASCADE,
    UNIQUE(outfit_id, item_id, item_role)
);

-- Seasonal Rotation Table
CREATE TABLE IF NOT EXISTS seasonal_rotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season TEXT NOT NULL,
    rotation_date DATE NOT NULL,
    items_active INTEGER,
    items_stored INTEGER,
    recommendations_json TEXT,
    CONSTRAINT check_season CHECK (season IN ('spring', 'summer', 'fall', 'winter'))
);

-- Agent Logs Table (for observability)
CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    success BOOLEAN,
    error_message TEXT,
    execution_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_wardrobe_type ON wardrobe_items(garment_type);
CREATE INDEX IF NOT EXISTS idx_wardrobe_color ON wardrobe_items(color);
CREATE INDEX IF NOT EXISTS idx_wardrobe_formality ON wardrobe_items(formality);
CREATE INDEX IF NOT EXISTS idx_outfits_date ON outfits(created_date);
CREATE INDEX IF NOT EXISTS idx_outfits_occasion ON outfits(occasion);
CREATE INDEX IF NOT EXISTS idx_feedback_outfit ON feedback_history(outfit_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON agent_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);

-- Create Views for Common Queries
CREATE VIEW IF NOT EXISTS wardrobe_summary AS
SELECT 
    garment_type,
    COUNT(*) as count,
    AVG(times_worn) as avg_worn,
    GROUP_CONCAT(DISTINCT color) as colors
FROM wardrobe_items
GROUP BY garment_type;

CREATE VIEW IF NOT EXISTS outfit_success_rate AS
SELECT 
    occasion,
    COUNT(*) as total_outfits,
    AVG(rating) as avg_rating,
    SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
FROM outfits
WHERE rating IS NOT NULL
GROUP BY occasion;

-- Insert Sample Data (Optional - for testing)
-- Uncomment to populate with demo data

/*
INSERT INTO user_preferences (gender, favorite_colors, disliked_colors, preferred_styles, sizes, preferences_json)
VALUES (
    'unisex',
    '["blue", "black", "white"]',
    '["orange", "yellow"]',
    '["modern", "minimalist"]',
    '{"shirt": "M", "pants": "32", "shoes": "10"}',
    '{"default_occasion": "casual", "city": "New York"}'
);
*/