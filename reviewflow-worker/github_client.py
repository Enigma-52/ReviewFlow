import time
import jwt  # pyjwt
import requests
from dataclasses import dataclass
from config import Settings


def load_private_key(private_key_path: str) -> str:
    with open(private_key_path, "r") as f:
        return f.read()


@dataclass
class GitHubAppClient:
    settings: Settings
    private_key: str

    def generate_app_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,  # issued slightly in past to avoid clock skew
            "exp": now + (10 * 60),  # valid for 10 minutes
            "iss": self.settings.github_app_id,
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_installation_token(self, installation_id: int) -> str:
        app_jwt = self.generate_app_jwt()
        url = (
            f"{self.settings.github_api_base}/app/installations/"
            f"{installation_id}/access_tokens"
        )
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
        }
        resp = requests.post(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["token"]

    def fetch_pr_diff(
        self, owner: str, repo: str, pr_id: int, installation_id: int
    ) -> str:
        token = self.get_installation_token(installation_id)
        url = f"{self.settings.github_api_base}/repos/{owner}/{repo}/pulls/{pr_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text

    def fetch_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str,
        installation_token: str,
    ) -> str:
        url = (
            f"{self.settings.github_api_base}/repos/{owner}/{repo}/contents/"
            f"{path}?ref={ref}"
        )
        headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github.v3.raw",
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 404:
            raise FileNotFoundError(f"File not found: {path}")
        resp.raise_for_status()
        return resp.text
