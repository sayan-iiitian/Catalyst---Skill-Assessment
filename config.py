"""
Configuration settings for the Catalyst Skill Assessment Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_MODEL = "deepseek-ai/deepseek-7b-chat"  # Lightweight, CPU-friendly
LLM_API_PROVIDER = "huggingface"  # Can be 'huggingface', 'ollama', 'local'
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Model Parameters
MAX_TOKENS = 1024
TEMPERATURE = 0.7
TOP_P = 0.95

# Assessment Configuration
MIN_SKILLS_TO_ASSESS = 3
MAX_SKILLS_TO_ASSESS = 10
ASSESSMENT_ROUNDS = 2  # Number of assessment questions per skill

# Learning Plan Configuration
LEARNING_PLAN_DEPTH = 3  # Number of learning recommendations per gap
TIME_ESTIMATE_MIN = 5  # Minimum hours for learning
TIME_ESTIMATE_MAX = 40  # Maximum hours for learning

# Application Settings
APP_NAME = "Catalyst - AI Skill Assessment & Learning Plan"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
