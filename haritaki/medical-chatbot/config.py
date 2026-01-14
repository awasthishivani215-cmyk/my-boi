# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Model Configuration
    GPT_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for faster responses
    
    # Medical API Keys (Placeholder - replace with actual APIs)
    MEDICAL_API_KEY = os.getenv("MEDICAL_API_KEY", "")
    SYMPTOM_CHECKER_API = os.getenv("SYMPTOM_CHECKER_API", "")
    
    # Paths
    PATIENT_RECORDS_PATH = "patient_records"
    REPORT_PATH = "reports"
    
    # App Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "medical-chatbot-secret-key-2024")
    DEBUG = os.getenv("DEBUG", True)
    
    # Chatbot Settings
    MAX_SYMPTOMS = 10
    MIN_SYMPTOMS = 1
    MAX_CONVERSATION_HISTORY = 20