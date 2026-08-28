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
CONTRACT_FIXTURE = _SCRIPTS / "validation" / "fixtures" / "contract-cases.json"


class ValidateArtRouterTests(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def load_contract_fixture(self) -> dict:
        return json.loads(CONTRACT_FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_covers_next_steps_cases(self) -> None:
        report = validate_manifest(self.load_fixture())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["case_count"], 7)
        self.assertEqual(report["passed"], 7)
        self.assertEqual(report["held"], 0)
        self.assertEqual(report["reasons"], [])
        self.assertTrue(all(case["reasons"] == [] for case in report["cases"]))
        self.assertTrue(all(not case["contract"]["present"] for case in report["cases"]))

    def test_contract_fixture_covers_common_artistic_request_classes(self) -> None:
        report = validate_manifest(self.load_contract_fixture())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["schema_version"], "1.1")
        self.assertEqual(report["case_count"], 3)
        self.assertEqual(report["passed"], 3)
        self.assertEqual(report["held"], 0)
        self.assertEqual(report["contract_summary"]["constraints"], {"preserved": 5, "unmet": 1, "unknown": 0})
        self.assertEqual(report["contract_summary"]["capabilities"], {"required": 6, "satisfied": 6, "unmet": 0})
        self.assertEqual(report["contract_summary"]["descriptor_drift"], 1)
        self.assertEqual(report["contract_summary"]["descriptor_regressions"], 1)
        self.assertIn("soft_constraint_unmet", {warning["code"] for warning in report["cases"][0]["warnings"]})
        self.assertEqual(report["cases"][0]["contract"]["capabilities"]["adapters"][1]["status"], "adapted")

    def test_hard_and_soft_unmet_are_distinguished(self) -> None:
        manifest = self.load_contract_fixture()
        constraints = manifest["cases"][0]["contract"]["constraints"]
        constraints[0]["delivered"] = "landscape"
        constraints[1]["delivered"] = "neon"

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}
        warning_codes = {warning["code"] for warning in result["warnings"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("hard_constraint_unmet", codes)
        self.assertIn("soft_constraint_unmet", warning_codes)
        self.assertEqual(result["contract"]["preserved"], 0)
        self.assertEqual(result["contract"]["unmet"], 2)
        self.assertEqual(result["contract"]["constraints"][0]["status"], "unmet")

    def test_ambiguity_and_conflict_hold(self) -> None:
        manifest = self.load_contract_fixture()
        contract = manifest["cases"][1]["contract"]
        contract["ambiguities"] = [{"id": "subject", "description": "Subject identity is unclear.", "status": "open"}]
        contract["conflicts"] = [{"id": "duration", "description": "Loop length conflicts with delivery limit.", "status": "unresolved"}]

        result = validate_manifest(manifest)["cases"][1]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("ambiguity_hold", codes)
        self.assertIn("conflict_hold", codes)
        self.assertEqual(result["contract"]["ambiguities"][0]["status"], "open")
        self.assertEqual(result["contract"]["conflicts"][0]["status"], "unresolved")

    def test_required_capability_must_be_available_or_adapted(self) -> None:
        manifest = self.load_contract_fixture()
        capabilities = manifest["cases"][2]["contract"]["capabilities"]
        capabilities["adapters"]["browser_preview"] = {"status": "unavailable"}
        del capabilities["adapters"]["reduced_motion"]

        result = validate_manifest(manifest)["cases"][2]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertEqual(result["contract"]["capabilities"]["unmet"], ["browser_preview", "reduced_motion"])
        self.assertIn("capability_unmet", codes)
        self.assertEqual(result["contract"]["capabilities"]["adapters"][1]["status"], "unreported")

    def test_descriptor_drift_and_baseline_regression_hold(self) -> None:
        manifest = self.load_contract_fixture()
        descriptors = manifest["cases"][1]["contract"]["descriptors"]
        descriptors["delivered"]["medium"] = "illustration"
        descriptors["baseline"] = {"medium": "animation", "loop": True}

        result = validate_manifest(manifest)["cases"][1]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("descriptor_drift", codes)
        self.assertIn("descriptor_regression", codes)
        self.assertEqual(result["contract"]["descriptors"]["drift"][0]["key"], "medium")
        self.assertEqual(result["contract"]["descriptors"]["regressions"][0]["key"], "medium")

    def test_schema_11_requires_contract_but_schema_10_does_not(self) -> None:
        manifest = self.load_fixture()
        manifest["schema_version"] = "1.1"

        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "hold")
        self.assertTrue(all("missing_value" in {reason["code"] for reason in case["reasons"]} for case in report["cases"]))

    def test_contract_reports_are_deterministic_and_text_is_safe(self) -> None:
        manifest = self.load_contract_fixture()
        manifest["cases"][0]["contract"]["constraints"][0]["id"] = "orientation\x1b[31m\nunsafe"
        manifest["cases"][0]["contract"]["constraints"][0]["delivered"] = "landscape"

        first = json.dumps(validate_manifest(manifest), sort_keys=True)
        second = json.dumps(validate_manifest(manifest), sort_keys=True)
        output = _text_report(validate_manifest(manifest))

        self.assertEqual(first, second)
        self.assertNotIn("\x1b", output)
        self.assertIn("orientation\\x1b[31m\\nunsafe", output)

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
