"""Tests for the art sample gallery package-path validator.

tags: [tests, validation, art-router, samples]
routing_hints: [sample-gallery, package-paths, representation-registry]
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
_REPO_ROOT = _SCRIPTS.parent
sys.path.insert(0, str(_SCRIPTS / "validation"))
from validate_art_samples import EXPECTED_PATHS, validate_sample_gallery  # noqa: E402

GALLERY_FIXTURE = _REPO_ROOT / "ai-tooling" / "skills" / "artistic" / "representation-routing" / "sample-gallery.json"


class ValidateArtSamplesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.gallery_path = self.root / "sample-gallery.json"
        self.gallery = json.loads(GALLERY_FIXTURE.read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_gallery(self) -> None:
        self.gallery_path.write_text(json.dumps(self.gallery), encoding="utf-8")

    def create_sample_files(self) -> None:
        for sample in self.gallery["samples"]:
            path = self.root / Path(*sample["path"].split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"test-only package file")

    def test_gallery_passes_when_all_reserved_paths_exist(self) -> None:
        self.create_sample_files()
        self.write_gallery()

        report = validate_sample_gallery(self.root, self.gallery_path)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["sample_count"], 6)
        self.assertEqual(set(report["checked_paths"]), EXPECTED_PATHS)

    def test_missing_sample_path_holds_gallery(self) -> None:
        self.create_sample_files()
        missing = self.gallery["samples"].pop(0)["path"]
        self.write_gallery()

        report = validate_sample_gallery(self.root, self.gallery_path)

        self.assertEqual(report["status"], "hold")
        self.assertTrue(any(missing in reason for reason in report["reasons"]))

    def test_traversal_path_is_rejected(self) -> None:
        self.gallery["samples"][0]["path"] = "../outside.png"
        self.write_gallery()

        report = validate_sample_gallery(self.root, self.gallery_path)

        self.assertEqual(report["status"], "hold")
        self.assertTrue(any("normalized repository-relative" in reason for reason in report["reasons"]))

    def test_route_and_asset_type_must_match(self) -> None:
        self.gallery["samples"][0]["asset_type"] = "vector_poster"
        self.create_sample_files()
        self.write_gallery()

        report = validate_sample_gallery(self.root, self.gallery_path)

        self.assertEqual(report["status"], "hold")
        self.assertTrue(any("not registered for representation 'collage'" in reason for reason in report["reasons"]))


if __name__ == "__main__":
    unittest.main()
