from dataclasses import dataclass
from app.core.config import settings


@dataclass
class CodeChunk:
    path: str
    text: str
    start_line: int
    end_line: int


def chunk_text(path: str, text: str) -> list[CodeChunk]:
    lines = text.splitlines()
    if not lines:
        return []
    size = max(settings.chunk_lines, 20)
    overlap = min(max(settings.chunk_overlap_lines, 0), size - 1)
    step = size - overlap
    chunks: list[CodeChunk] = []
    start = 0
    while start < len(lines):
        end = min(start + size, len(lines))
        body = "\n".join(lines[start:end]).strip()
        if body:
            chunks.append(CodeChunk(path=path, text=body, start_line=start + 1, end_line=end))
        if end == len(lines):
            break
        start += step
    return chunks
