"""Configuration settings for AI Fashion Consultant"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/wardrobe.db")

# App Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ==============================================================================
#  MODEL ARCHITECTURE
# ==============================================================================
# DESIGN DECISION: "High-Fidelity" Hybrid Strategy
# We combine the deepest reasoning model with the newest, fastest vision model.

# 1. THE BRAIN: Reasoning Model
# Used by: PlannerAgent, RecommenderAgent, FeedbackAgent
# Model: Gemini 2.0 Flash Experimental
# Justification: Provides the highest quality reasoning for style rules, 
# constraints, and complex user instruction following.
GEMINI_MODEL = "gemini-2.0-flash"

# . THE EYES: Perception Model
# Used by: PerceptionAgent (Image Ingestion Pipeline)
# Model: Gemini 2.0 Flash Experimental
# Justification: 2.0 Flash offers a superior balance of speed and visual accuracy.
# It resolves the "429 Resource Exhausted" errors seen with 1.5 Pro during batch 
# uploads, but maintains higher visual fidelity than "Flash-Lite" for identifying 
# subtle fabric textures and patterns.
GEMINI_VISION_MODEL = "gemini-2.0-flash"

# ==============================================================================

TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Agent Settings
MAX_RETRIES = 3
AGENT_TIMEOUT = 30  # seconds

# Fashion Rules
GENDER_PROFILES = ["male", "female", "unisex"]
OCCASIONS = [
    "casual",
    "work",
    "wedding",
    "party",
    "formal",
    "travel",
    "date",
    "festival"
]

SEASONS = ["spring", "summer", "fall", "winter"]

# Color Matching Rules
COLOR_COMPLEMENTARY = {
    "blue": ["orange", "yellow", "white", "beige"],
    "red": ["green", "white", "black", "navy"],
    "green": ["red", "brown", "beige", "white"],
    "yellow": ["purple", "blue", "gray", "white"],
    "purple": ["yellow", "green", "white", "gold"],
    "orange": ["blue", "teal", "white", "brown"],
    "pink": ["gray", "white", "navy", "green"],
    "brown": ["cream", "beige", "white", "blue"],
    "black": ["white", "red", "gold", "pink"],
    "white": ["any"],
    "gray": ["any"]
}

# Wardrobe Settings
MIN_WARDROBE_ITEMS = 5
WARDROBE_UTILIZATION_TARGET = 0.6  # 60%

# Memory Settings
MEMORY_RETENTION_DAYS = 90
FEEDBACK_WEIGHT = 0.8

print(f"✓ Settings loaded - Environment: {ENVIRONMENT}")