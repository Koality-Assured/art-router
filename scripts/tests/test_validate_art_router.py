"""Focused tests for the portable art-router manifest validator.

tags: [tests, validation, art-router]
routing_hints: [manifest, fixtures, provenance, accessibility, delivery, review]

Run: python -m unittest scripts.tests.test_validate_art_router -v
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS / "validation"))

from validate_art_router import (  # noqa: E402
    _text_report,
    main,
    validate_manifest,
)


FIXTURE = _SCRIPTS / "validation" / "fixtures" / "next-steps.json"


class ValidateArtRouterTests(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_covers_next_steps_cases(self) -> None:
        report = validate_manifest(self.load_fixture())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["case_count"], 7)
        self.assertEqual(report["passed"], 7)
        self.assertEqual(report["held"], 0)
        self.assertEqual(report["reasons"], [])
        self.assertTrue(all(case["reasons"] == [] for case in report["cases"]))

    def test_missing_controls_and_measurement_hold_with_reasons(self) -> None:
        manifest = self.load_fixture()
        case = manifest["cases"][0]
        del case["intent"]["audience"]
        case["measurements"]["width_px"] = 10
        case["reviewer"]["decision"] = "hold"

        report = validate_manifest(manifest)
        result = report["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(report["status"], "hold")
        self.assertEqual(result["status"], "hold")
        self.assertIn("missing_value", codes)
        self.assertIn("criterion_failed", codes)
        self.assertIn("review_hold", codes)

    def test_rights_and_declared_safety_holds_are_not_silently_ignored(self) -> None:
        manifest = self.load_fixture()
        case = manifest["cases"][3]
        case["provenance"]["rights_status"] = "unknown"
        case["checks"]["safety"]["status"] = "hold"

        result = validate_manifest(manifest)["cases"][3]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("rights_hold", codes)
        self.assertIn("declared_check_hold", codes)

    def test_asset_reference_is_informational_and_no_file_is_required(self) -> None:
        manifest = self.load_fixture()
        manifest["cases"][0]["asset"]["reference"] = "this-file-does-not-exist.png"

        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "pass")
        self.assertIn("asset existence", report["scope_note"])

    def test_non_object_and_duplicate_cases_hold(self) -> None:
        manifest = self.load_fixture()
        manifest["cases"].append("untrusted scalar")
        manifest["cases"].append(dict(manifest["cases"][0]))
        manifest["cases"][-1]["id"] = manifest["cases"][0]["id"]

        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "hold")
        self.assertEqual(report["cases"][7]["status"], "hold")
        self.assertIn("invalid_type", {r["code"] for r in report["cases"][7]["reasons"]})
        self.assertIn("duplicate_id", {r["code"] for r in report["cases"][8]["reasons"]})

    def test_cli_json_and_fail_on_hold(self) -> None:
        manifest = self.load_fixture()
        manifest["cases"][1]["measurements"]["monochrome_tested"] = False
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            output = io.StringIO()
            errors = io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                rc = main(["--manifest", str(path), "--json", "--fail-on-hold"])

        self.assertEqual(rc, 1)
        self.assertEqual(errors.getvalue(), "")
        report = json.loads(output.getvalue())
        self.assertEqual(report["status"], "hold")
        self.assertIn("criterion_failed", {r["code"] for r in report["cases"][1]["reasons"]})

    def test_reports_are_deterministic(self) -> None:
        manifest = self.load_fixture()

        first = json.dumps(validate_manifest(manifest), sort_keys=True)
        second = json.dumps(validate_manifest(manifest), sort_keys=True)

        self.assertEqual(first, second)

    def test_text_report_sanitizes_untrusted_identifiers(self) -> None:
        manifest = self.load_fixture()
        manifest["manifest_id"] = "manifest\x1b[31m\ninjection"
        manifest["cases"][0]["id"] = "case\x1b[32m\ninjection"

        output = _text_report(validate_manifest(manifest))

        self.assertNotIn("\x1b", output)
        self.assertIn("manifest: manifest\\x1b[31m\\ninjection", output)
        self.assertIn("- case\\x1b[32m\\ninjection (illustration)", output)


if __name__ == "__main__":
    unittest.main()
