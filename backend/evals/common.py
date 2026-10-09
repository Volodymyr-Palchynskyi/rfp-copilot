import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

EVALS_DIR = Path(__file__).parent
RESULTS_DIR = EVALS_DIR / "results"

CATEGORIES = ["close_analog", "partial_overlap", "out_of_domain"]


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    brief: str
    expected_projects: list[str]
    hours_range: tuple[int, int]

    @property
    def expected_mid(self) -> float:
        return sum(self.hours_range) / 2


def load_cases() -> list[Case]:
    raw = json.loads((EVALS_DIR / "cases.json").read_text(encoding="utf-8"))
    return [
        Case(
            id=c["id"],
            category=c["category"],
            brief=c["brief"],
            expected_projects=c["expected_projects"],
            hours_range=tuple(c["hours_range"]),
        )
        for c in raw
    ]


def md_table(headers: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def save_report(name: str, markdown: str, data: dict) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (RESULTS_DIR / f"{name}.md").write_text(f"_Generated {stamp}_\n\n{markdown}\n", encoding="utf-8")
    (RESULTS_DIR / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
