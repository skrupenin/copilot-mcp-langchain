"""
Configuration settings for Teams Adaptive Cards Fixer
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Azure AD Settings
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET') 
    TENANT_ID = os.getenv('TENANT_ID')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080/auth/callback')
    
    # Microsoft Graph Settings
    GRAPH_API_BASE = os.getenv('GRAPH_API_BASE', 'https://graph.microsoft.com/v1.0')
    SCOPES = os.getenv('SCOPES', 'https://graph.microsoft.com/Chat.ReadWrite https://graph.microsoft.com/User.Read').split()
    
    # Application Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = ['CLIENT_ID', 'CLIENT_SECRET', 'TENANT_ID']
        missing = [field for field in required_fields if not getattr(cls, field)]
        
        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            print("Please check your .env file or environment variables")
            return False
        
        return True
    
    @classmethod
    def get_authority(cls) -> str:
        """Get Azure AD authority URL"""
        return f"https://login.microsoftonline.com/{cls.TENANT_ID}"
