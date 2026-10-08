"""Regression checks for captured official sources used by art routing.

tags: [tests, validation, art-router, references]
routing_hints: [art-references, source-status, official-source-capture]
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPOSITORY_ROOT / "references" / "artistic" / "source-catalog.json"


class ArtReferenceCatalogTests(unittest.TestCase):
    def test_official_source_catalog_matches_capture_and_preserves_status(self) -> None:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(catalog["schema_version"], "1.0")
        self.assertEqual(catalog["family"], "artistic")
        self.assertTrue(catalog["advisory_only"])

        capture_path = (CATALOG_PATH.parent / catalog["source_capture"]).resolve(strict=True)
        capture_path.relative_to(REPOSITORY_ROOT.resolve())
        capture = capture_path.read_text(encoding="utf-8")
        capture_metadata = capture.split("---", 2)[1].splitlines()
        captured_at = next(line.split(":", 1)[1].strip() for line in capture_metadata if line.startswith("captured_at_utc:"))
        self.assertEqual(catalog["captured_at_utc"], captured_at)
        sources = {source["id"]: source for source in catalog["sources"]}
        self.assertEqual(
            set(sources),
            {
                "w3c-epub-a11y-11",
                "w3c-epub-a11y-12-crd",
                "iso-9241-910-2011",
                "iso-9241-920-2024",
                "khronos-openxr-1-1",
            },
        )

        for source in sources.values():
            self.assertTrue(
                source["official_url"].startswith(
                    ("https://www.w3.org/", "https://www.iso.org/", "https://registry.khronos.org/")
                )
            )
            self.assertIn(source["id"], capture)
            for url in (source["official_url"], source.get("version_url", ""), *source.get("related_urls", [])):
                if url:
                    self.assertIn(url, capture)

        self.assertEqual(sources["w3c-epub-a11y-11"]["status"], "Recommendation")
        self.assertEqual(sources["w3c-epub-a11y-11"]["status_date"], "2024-10-17")
        self.assertEqual(sources["w3c-epub-a11y-12-crd"]["status"], "Candidate Recommendation Draft")
        self.assertEqual(sources["w3c-epub-a11y-12-crd"]["status_date"], "2026-09-12")

        framework = sources["iso-9241-910-2011"]
        requirements = sources["iso-9241-920-2024"]
        self.assertIn("Current", framework["status"])
        self.assertEqual(framework["status_date"], "2022-06-30")
        self.assertIn("metadata only", framework["scope"])
        self.assertIn("ISO Open Data", framework["source_use_note"])
        self.assertIn("current", requirements["status"].casefold())
        self.assertEqual(requirements["status_date"], "2024-10-11")
        self.assertEqual(requirements["previous_version"], "ISO 9241-920:2009 (withdrawn)")
        self.assertIn("metadata only", requirements["scope"])
        self.assertIn("ISO Open Data", requirements["source_use_note"])
        self.assertEqual(sources["khronos-openxr-1-1"]["version"], "1.1.63")
        self.assertTrue(
            any("xrApplyHapticFeedback" in url for url in sources["khronos-openxr-1-1"]["related_urls"])
        )


if __name__ == "__main__":
    unittest.main()
