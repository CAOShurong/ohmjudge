from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_exist(self) -> None:
        markdown_files = [
            *ROOT.glob("*.md"),
            *ROOT.glob("docs/**/*.md"),
            *ROOT.glob("demo/*.md"),
            *ROOT.glob("examples/*.md"),
        ]
        missing: list[str] = []
        for path in markdown_files:
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                clean = target.strip().strip("<>").split("#", 1)[0]
                if not clean or "://" in clean or clean.startswith("mailto:"):
                    continue
                destination = (path.parent / clean).resolve()
                if not destination.exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual([], missing)

    def test_repository_copy_contains_no_cjk_prose(self) -> None:
        paths = [
            *ROOT.glob("*.md"),
            *ROOT.glob("docs/**/*"),
            *ROOT.glob("site/**/*"),
            *ROOT.glob(".github/**/*"),
        ]
        offenders: list[str] = []
        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
