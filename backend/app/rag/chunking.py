import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SECTION = re.compile(r"^## (.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    payload: dict = field(default_factory=dict)


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER.match(raw)
    if not match:
        return {}, raw
    meta = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        if key.strip():
            meta[key.strip()] = value.strip()
    return meta, raw[match.end():]


def chunk_document(path: Path) -> list[Chunk]:
    """
    Structure-aware chunking: one chunk per `## Section`.

    Sections in these documents are short and self-contained (scope list, risks),
    so splitting on headings keeps related facts together better than fixed-size windows.
    Every chunk is prefixed with the project title so that it stays meaningful
    when retrieved on its own, and carries the project metadata as payload.
    """
    meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
    project_id = meta.get("id", path.stem)

    headings = list(_SECTION.finditer(body))
    chunks: list[Chunk] = []
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section = heading.group(1).strip()
        content = body[heading.end():end].strip()
        if not content:
            continue

        chunks.append(
            Chunk(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{project_id}#{section}")),
                text=f"{meta.get('title', project_id)} ({meta.get('industry', 'n/a')}) - {section}\n{content}",
                payload={
                    "project_id": project_id,
                    "title": meta.get("title", project_id),
                    "industry": meta.get("industry", ""),
                    "stack": meta.get("stack", ""),
                    "duration_weeks": int(meta.get("duration_weeks", 0) or 0),
                    "total_hours": int(meta.get("total_hours", 0) or 0),
                    "section": section,
                    "source": path.name,
                },
            )
        )
    return chunks


def load_corpus(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_document(path))
    return chunks
