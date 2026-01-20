"""
Configuration management for WealthBridge Tradeline MCP.
Loads from .env and provides typed access to all settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Literal

# Load .env from repo root
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

Environment = Literal["development", "staging", "production"]

class Config:
    """Central configuration for WealthBridge Tradeline MCP."""
    
    # Environment
    ENVIRONMENT: Environment = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
    
    # Credit Bureau APIs
    EXPERIAN_API_KEY = os.getenv("EXPERIAN_API_KEY", "")
    EXPERIAN_BASE_URL = os.getenv("EXPERIAN_BASE_URL", "https://api.experian.com/business/v1")
    EXPERIAN_CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID", "")
    EXPERIAN_CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET", "")
    
    EQUIFAX_API_KEY = os.getenv("EQUIFAX_API_KEY", "")
    EQUIFAX_BASE_URL = os.getenv("EQUIFAX_BASE_URL", "https://api.equifax.com/business/v1")
    
    DUNS_API_KEY = os.getenv("DUNS_API_KEY", "")
    DUNS_BASE_URL = os.getenv("DUNS_BASE_URL", "https://api.dnb.com/v1")
    
    # Payment Processors
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    
    # Alternative Data
    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET = os.getenv("PLAID_SECRET", "")
    PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")
    
    # Federal API Integration
    FEDERAL_VAULT_URL = os.getenv("FEDERAL_VAULT_URL", "http://localhost:8000")
    FEDERAL_VAULT_API_KEY = os.getenv("FEDERAL_VAULT_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/tradeline.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Tradeline Reporting
    AUTO_REPORT_ENABLED = os.getenv("AUTO_REPORT_ENABLED", "true").lower() == "true"
    REPORT_FREQUENCY_DAYS = int(os.getenv("REPORT_FREQUENCY_DAYS", "30"))
    MINIMUM_PAYMENT_AMOUNT = float(os.getenv("MINIMUM_PAYMENT_AMOUNT", "100.00"))
    MINIMUM_ACCOUNT_AGE_DAYS = int(os.getenv("MINIMUM_ACCOUNT_AGE_DAYS", "90"))
    
    # Credit Scoring
    SCORING_MODEL = os.getenv("SCORING_MODEL", "wealthbridge_v1")
    WEIGHT_PAYMENT_HISTORY = int(os.getenv("WEIGHT_PAYMENT_HISTORY", "35"))
    WEIGHT_CREDIT_UTILIZATION = int(os.getenv("WEIGHT_CREDIT_UTILIZATION", "30"))
    WEIGHT_CREDIT_AGE = int(os.getenv("WEIGHT_CREDIT_AGE", "15"))
    WEIGHT_CREDIT_MIX = int(os.getenv("WEIGHT_CREDIT_MIX", "10"))
    WEIGHT_NEW_CREDIT = int(os.getenv("WEIGHT_NEW_CREDIT", "10"))
    
    # Compliance
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # 7 years
    PII_ENCRYPTION_ENABLED = os.getenv("PII_ENCRYPTION_ENABLED", "true").lower() == "true"
    AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
    RATE_LIMIT_TRADELINE_PULLS_PER_DAY = int(os.getenv("RATE_LIMIT_TRADELINE_PULLS_PER_DAY", "50"))
    
    # Notifications
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/tradeline.log")
    
    # Feature Flags
    ENABLE_MANUAL_TRADELINE_CREATION = os.getenv("ENABLE_MANUAL_TRADELINE_CREATION", "true").lower() == "true"
    ENABLE_FEDERAL_CONTRACT_TRACKING = os.getenv("ENABLE_FEDERAL_CONTRACT_TRACKING", "true").lower() == "true"
    ENABLE_AI_CREDIT_RECOMMENDATIONS = os.getenv("ENABLE_AI_CREDIT_RECOMMENDATIONS", "true").lower() == "true"
    ENABLE_VENDOR_CREDIT_PROGRAM = os.getenv("ENABLE_VENDOR_CREDIT_PROGRAM", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Returns list of missing critical configurations."""
        missing = []
        
        # Critical for production
        if cls.ENVIRONMENT == "production":
            if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-change-me":
                missing.append("SECRET_KEY (production requires unique key)")
            if not cls.ENCRYPTION_KEY:
                missing.append("ENCRYPTION_KEY (required for PII encryption)")
        
        # At least one credit bureau required
        if not any([cls.EXPERIAN_API_KEY, cls.EQUIFAX_API_KEY, cls.DUNS_API_KEY]):
            missing.append("At least one credit bureau API key (EXPERIAN, EQUIFAX, or DUNS)")
        
        return missing
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.ENVIRONMENT == "development"
