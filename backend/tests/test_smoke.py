from app.services.github import parse_github_url, should_index
from app.services.repo_parser import chunk_text


def test_parse_github_url():
    ref = parse_github_url("https://github.com/openai/openai-python")
    assert ref.owner == "openai"
    assert ref.name == "openai-python"


def test_should_index_source_files():
    assert should_index("app/main.py")
    assert should_index("package.json")
    assert not should_index("node_modules/pkg/index.js")
    assert not should_index("assets/logo.png")


def test_chunk_text():
    text = "\n".join(f"line {i}" for i in range(250))
    chunks = chunk_text("x.py", text)
    assert len(chunks) >= 3
    assert chunks[0].start_line == 1
