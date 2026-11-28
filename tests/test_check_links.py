from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_links.py"
SPEC = importlib.util.spec_from_file_location("check_links", SCRIPT)
check_links = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(check_links)


class CheckLinksTests(unittest.TestCase):
    def test_original_page_fails_and_fixed_page_passes(self) -> None:
        original = Path(__file__).resolve().parents[1] / "5k-sprint" / "index.html"
        source = original.read_text(encoding="utf-8")
        old_page = source.replace('href="https://calendly.com/rg2official/15min"', 'href="PAYLINK_600"', 1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "5k-sprint" / "index.html"
            page.parent.mkdir()
            page.write_text(old_page, encoding="utf-8")
            self.assertTrue(check_links.check_site(root), "the original placeholder must fail")
            page.write_text(source, encoding="utf-8")
            self.assertEqual([], check_links.check_site(root))


if __name__ == "__main__":
    unittest.main()
