"""
Configuration management for the ETL pipeline.
Loads environment variables and provides configuration to other modules.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Central configuration class."""
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Mercury API
    MERCURY_API_KEY = os.getenv("MERCURY_API_KEY", "mock_key")
    
    # QuickBooks API
    QUICKBOOKS_CLIENT_ID = os.getenv("QUICKBOOKS_CLIENT_ID", "mock_id")
    QUICKBOOKS_CLIENT_SECRET = os.getenv("QUICKBOOKS_CLIENT_SECRET", "mock_secret")
    QUICKBOOKS_REFRESH_TOKEN = os.getenv("QUICKBOOKS_REFRESH_TOKEN", "mock_token")
    QUICKBOOKS_REALM_ID = os.getenv("QUICKBOOKS_REALM_ID") 
    
    # GitHub API
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "mock_token")
    GITHUB_ORG = os.getenv("GITHUB_ORG", "your-org")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "your-repo")
    
    # Slack
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
    SLACK_WEBHOOK_URL_2 = os.getenv("SLACK_WEBHOOK_URL_2", "")  # Optional second channel
    SLACK_WEBHOOK_URL_3 = os.getenv("SLACK_WEBHOOK_URL_3", "")  # Optional third channel
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required = {
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_KEY": cls.SUPABASE_KEY,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

# Validate config on import
Config.validate()
