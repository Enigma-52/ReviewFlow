import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    redis_url: str
    github_app_id: str
    github_private_key_path: str
    github_api_base: str
    db_url: Optional[str]
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str


settings = Settings(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
    github_app_id=require_env("GITHUB_APP_ID"),
    github_private_key_path=require_env("GITHUB_PRIVATE_KEY_PATH"),
    github_api_base=os.getenv("GITHUB_API_BASE", "https://api.github.com"),
    db_url=os.getenv("DATABASE_URL"),
    db_host=os.getenv("DB_HOST", "localhost"),
    db_port=int(os.getenv("DB_PORT", "5432")),
    db_name=os.getenv("DB_NAME", "reviewflow"),
    db_user=os.getenv("DB_USER", "reviewflow"),
    db_password=os.getenv("DB_PASSWORD", "reviewflow"),
)
