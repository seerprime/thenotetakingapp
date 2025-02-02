from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database configurations
DATABASE_PATH = os.path.join(BASE_DIR, "database", "notes.db")
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "database", "vector_store.faiss")

# Model configurations
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gpt-3.5-turbo"  # Change as needed

# API configurations
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Audio configurations
ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "ogg"}
MAX_AUDIO_LENGTH = 600  # Maximum audio length in seconds
SAMPLE_RATE = 16000

# RAG configurations
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3

# Summary configurations
MAX_SUMMARY_LENGTH = 500
MIN_SUMMARY_LENGTH = 100

class Config:
    # Flask configurations
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # CORS configurations
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Database configurations
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configurations
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)

# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True

# Production configuration
class ProductionConfig(Config):
    DEBUG = False

# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}