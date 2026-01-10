# configuración de variables de entorno
import os
from dotenv import load_dotenv

load_dotenv()  

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("❌ GITHUB_TOKEN not found. Check your .env file.")

MODEL_NAME = os.getenv("GITHUB_MODEL", "gpt-4o")
