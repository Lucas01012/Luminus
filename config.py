# Configurações globais para performance
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações de performance
PERFORMANCE_CONFIG = {
    # Timeouts em segundos
    'API_TIMEOUT': 10,
    'GEMINI_TIMEOUT': 8,
    'VISION_TIMEOUT': 15,
    
    # Compressão de imagens
    'MAX_IMAGE_SIZE': (512, 512),
    'IMAGE_QUALITY': 70,
    'ULTRA_FAST_SIZE': (256, 256),
    'ULTRA_FAST_QUALITY': 30,
    
    # Configurações do Gemini
    'GEMINI_MAX_TOKENS': 150,
    'GEMINI_TEMPERATURE': 0.1,
    'GEMINI_TOP_P': 0.8,
    'GEMINI_TOP_K': 20,
}

# Configurações de API
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")