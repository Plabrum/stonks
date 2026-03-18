import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv("../.env.local")  # fallback when running from project root


@dataclass
class Config:
    # ─── App ──────────────────────────────────────────────────────────────────
    ENV: str = os.getenv("ENV", "development")

    # ─── CORS ─────────────────────────────────────────────────────────────────
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # ─── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ─── Static files ─────────────────────────────────────────────────────────
    STATIC_DIR: str = os.getenv("STATIC_DIR", "frontend/dist")

    # ─── Computed properties ───────────────────────────────────────────────────

    @property
    def IS_DEV(self) -> bool:
        return self.ENV == "development"

    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL", "postgresql+asyncpg://litestar:password@localhost/app")
        if not url.startswith("postgresql+asyncpg"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def ADMIN_DB_URL(self) -> str:
        return os.getenv("ADMIN_DB_URL", "postgresql://litestar:password@localhost/app")


@dataclass
class DevelopmentConfig(Config):
    ENV: str = "development"


@dataclass
class ProductionConfig(Config):
    ENV: str = "production"


def get_config() -> Config:
    env = os.getenv("ENV", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()


# Global singleton — imported by factory.py and alembic/env.py
config = get_config()
