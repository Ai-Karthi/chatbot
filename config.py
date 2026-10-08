import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _path(value):
    
    return value if os.path.isabs(value) else os.path.join(BASE_DIR, value)


MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

TOP_K = int(os.getenv("TOP_K", "4"))

HANDBOOK_PATH = _path(os.getenv("HANDBOOK_PATH", "technova_handbook.txt"))

CHROMA_PATH = _path(os.getenv("CHROMA_PATH", "chroma_db"))

HISTORY_PATH = _path(os.getenv("HISTORY_PATH", "chat_history.json"))

WELCOME_AUDIO = _path(os.path.join("assets", "welcome.mp3"))

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "TechNova_handbook")

MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "180"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

HISTORY_WINDOW = int(os.getenv("HISTORY_WINDOW", "6"))

APP_NAME = "TechNova AI Voice Assistant"
COMPANY_NAME = "TechNova Solutions"
