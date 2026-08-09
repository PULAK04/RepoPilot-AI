import re
import base64
from dataclasses import dataclass
from urllib.parse import urlparse
import httpx
from app.core.config import settings

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".cpp", ".cc", ".c", ".h", ".hpp",
    ".cs", ".php", ".rb", ".kt", ".kts", ".swift", ".sql", ".html", ".css", ".scss", ".vue", ".svelte",
    ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini", ".env.example", ".dockerfile", ".sh"
}
SPECIAL_NAMES = {
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "package.json", "requirements.txt",
    "pyproject.toml", "Pipfile", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "README.md"
}
SKIP_PARTS = {
    "node_modules", ".git", "dist", "build", ".next", ".venv", "venv", "vendor", "coverage",
    "__pycache__", ".idea", ".vscode", "target"
}


@dataclass
class RepoRef:
    owner: str
    name: str


def parse_github_url(url: str) -> RepoRef:
    parsed = urlparse(url)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Only github.com repository URLs are supported")
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError("Expected a GitHub URL like https://github.com/owner/repository")
    owner, name = parts[0], re.sub(r"\.git$", "", parts[1])
    if not owner or not name:
        raise ValueError("Invalid GitHub repository URL")
    return RepoRef(owner=owner, name=name)


def should_index(path: str) -> bool:
    parts = path.split("/")
    if any(part in SKIP_PARTS for part in parts):
        return False
    name = parts[-1]
    if name in SPECIAL_NAMES:
        return True
    dot = "." + name.split(".")[-1].lower() if "." in name else ""
    return dot in SUPPORTED_EXTENSIONS


class GitHubService:
    def __init__(self):
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        self.client = httpx.Client(base_url="https://api.github.com", headers=headers, timeout=30.0)

    def repo_info(self, owner: str, name: str) -> dict:
        r = self.client.get(f"/repos/{owner}/{name}")
        r.raise_for_status()
        return r.json()

    def list_files(self, owner: str, name: str, branch: str) -> list[dict]:
        r = self.client.get(f"/repos/{owner}/{name}/git/trees/{branch}", params={"recursive": "1"})
        r.raise_for_status()
        tree = r.json().get("tree", [])
        files = [x for x in tree if x.get("type") == "blob" and should_index(x.get("path", ""))]
        return files[: settings.max_repo_files]

    def get_text_file(self, owner: str, name: str, path: str, branch: str) -> str | None:
        # The Contents API works for public repositories and, with GITHUB_TOKEN, private repositories.
        r = self.client.get(f"/repos/{owner}/{name}/contents/{path}", params={"ref": branch})
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("type") != "file" or data.get("encoding") != "base64":
            return None
        if int(data.get("size") or 0) > settings.max_file_bytes:
            return None
        try:
            raw = base64.b64decode(data.get("content", ""), validate=False)
            if len(raw) > settings.max_file_bytes:
                return None
            return raw.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return None
