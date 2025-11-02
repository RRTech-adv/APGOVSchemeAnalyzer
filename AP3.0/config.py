import os
from typing import Optional

class Settings:
    # Gemini API Configuration
    GEMINI_API_URL: str = "https://genai-sharedservice-americas.pwc.com/completions"
    GEMINI_API_KEY: str = "sk-SxXiWpNEB1MCA_yxD3eHiQ"
    GEMINI_MODEL: str = "vertex_ai.gemini-2.0-flash"
    
    # Database Configuration
    DATABASE_PATH: str = "arunachal_schemes.db"
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    
    @property
    def gemini_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "API-Key": self.GEMINI_API_KEY,
            "Authorization": f"Bearer {self.GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }

settings = Settings()

