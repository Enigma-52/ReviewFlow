import os
from dataclasses import dataclass
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


settings = Settings(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
    github_app_id=require_env("GITHUB_APP_ID"),
    github_private_key_path=require_env("GITHUB_PRIVATE_KEY_PATH"),
    github_api_base=os.getenv("GITHUB_API_BASE", "https://api.github.com"),
)
