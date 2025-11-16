"""
Configuration Management for Agnovat Analyst MCP Server
Uses pydantic-settings for environment variable management
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    APP_NAME: str = "Agnovat Analyst MCP Server"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # Security Settings
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Secret key for authentication",
    )
    API_KEY_ENABLED: bool = Field(default=False, description="Enable API key authentication")

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024, description="Max upload size in bytes (50MB)")
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory path")
    TEMP_DIR: str = Field(default="./temp", description="Temporary files directory")

    # PDF Processing Settings
    PDF_MAX_PAGES: int = Field(default=500, description="Maximum pages per PDF")
    PDF_EXTRACT_IMAGES: bool = Field(default=False, description="Extract images from PDFs")

    # NLP Model Settings
    SPACY_MODEL: str = Field(default="en_core_web_sm", description="spaCy model name")
    TRANSFORMERS_MODEL: str = Field(
        default="bert-base-uncased",
        description="Transformers model for bias detection",
    )
    USE_GPU: bool = Field(default=False, description="Use GPU for ML models")

    # Analysis Thresholds
    BIAS_THRESHOLD: float = Field(default=0.7, description="Bias detection threshold (0-1)")
    SIMILARITY_THRESHOLD: float = Field(default=0.85, description="Document similarity threshold")
    TEMPLATE_REUSE_THRESHOLD: float = Field(
        default=0.75, description="Template reuse detection threshold"
    )

    # Legal Framework Settings
    JURISDICTION: str = Field(default="QLD", description="Legal jurisdiction (QLD)")
    LEGAL_ACTS: List[str] = Field(
        default=[
            "Guardianship and Administration Act 2000 (Qld)",
            "Human Rights Act 2019 (Qld)",
            "Anti-Discrimination Act 1991 (Qld)",
            "NDIS Act 2013",
            "Racial Discrimination Act 1975 (Cth)",
        ],
        description="Relevant legal acts",
    )

    # NDIS Goals Configuration
    NDIS_GOALS: List[str] = Field(
        default=[
            "G1: Business & Independence",
            "G2: Emotional Regulation & Communication",
            "G3: Family & Community Relationships",
            "G4: Cultural Responsibilities",
            "G5: Independent Living Skills",
            "G6: Sexual Relationships & Education",
            "G7: Community Participation & Social Networks",
        ],
        description="NDIS goal categories",
    )

    # Report Generation Settings
    REPORT_OUTPUT_DIR: str = Field(default="./reports", description="Report output directory")
    REPORT_TEMPLATE_DIR: str = Field(default="./templates", description="Report template directory")
    GENERATE_PDF_REPORTS: bool = Field(default=True, description="Generate PDF reports")

    # Chain of Custody Settings
    ENABLE_HASHING: bool = Field(default=True, description="Enable document hashing")
    HASH_ALGORITHM: str = Field(default="sha256", description="Hash algorithm")
    ENABLE_TIMESTAMPS: bool = Field(default=True, description="Enable timestamping")


# Create global settings instance
settings = Settings()
