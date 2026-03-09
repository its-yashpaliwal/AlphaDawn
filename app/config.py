"""
Application configuration — loaded from environment / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central settings object, populated from .env or environment variables."""

    # ── App ──
    app_env: str = Field("development", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    # ── Database ──
    database_url: str = Field(
        "postgresql+asyncpg://user:password@localhost:5432/alphadawn",
        alias="DATABASE_URL",
    )
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")

    # ─── AI / LLM ───
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    gemini_api_key: str = Field("", alias="GEMINI_API_KEY")
    groq_api_key: str = Field("", alias="GROQ_API_KEY")

    # Model defaults
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
    gemini_model: str = Field("gemini-1.5-flash", alias="GEMINI_MODEL")
    groq_model: str = Field("llama-3.1-8b-instant", alias="GROQ_MODEL")

    # ── News Sources ──
    twitter_bearer_token: str = Field("", alias="TWITTER_BEARER_TOKEN")
    moneycontrol_base_url: str = Field(
        "https://www.moneycontrol.com", alias="MONEYCONTROL_BASE_URL"
    )
    et_base_url: str = Field(
        "https://economictimes.indiatimes.com", alias="ET_BASE_URL"
    )
    business_standard_base_url: str = Field(
        "https://www.business-standard.com", alias="BUSINESS_STANDARD_BASE_URL"
    )

    # ── Exchange APIs ──
    bse_api_url: str = Field("https://api.bseindia.com", alias="BSE_API_URL")
    nse_api_url: str = Field("https://www.nseindia.com/api", alias="NSE_API_URL")

    # ── Market Data ──
    sgx_nifty_url: str = Field("", alias="SGX_NIFTY_URL")
    yahoo_finance_api_key: str = Field("", alias="YAHOO_FINANCE_API_KEY")

    # ── Telegram ──
    telegram_bot_token: str = Field("", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field("", alias="TELEGRAM_CHAT_ID")

    # ── Email ──
    smtp_host: str = Field("smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_user: str = Field("", alias="SMTP_USER")
    smtp_password: str = Field("", alias="SMTP_PASSWORD")
    email_recipients: str = Field("", alias="EMAIL_RECIPIENTS")

    # ── Scheduler ──
    pre_market_run_cron: str = Field("0 7 * * 1-5", alias="PRE_MARKET_RUN_CRON")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton settings instance
settings = Settings()
