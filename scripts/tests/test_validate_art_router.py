"""Focused tests for the portable art-router manifest validator.

tags: [tests, validation, art-router]
routing_hints: [manifest, fixtures, provenance, accessibility, delivery, review, request-contract]

Run: python -m unittest scripts.tests.test_validate_art_router -v
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS / "validation"))

from validate_art_router import (  # noqa: E402
    MEDIUM_CRITERIA,
    REPRESENTATION_ROWS,
    _resolve_medium,
    _text_report,
    main,
    validate_manifest,
)


FIXTURE = _SCRIPTS / "validation" / "fixtures" / "next-steps.json"
CONTRACT_FIXTURE = _SCRIPTS / "validation" / "fixtures" / "contract-cases.json"
MEDIA_FIXTURE = _SCRIPTS / "validation" / "fixtures" / "portfolio-brand-media.json"


class ValidateArtRouterTests(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def load_contract_fixture(self) -> dict:
        return json.loads(CONTRACT_FIXTURE.read_text(encoding="utf-8"))

    def load_media_fixture(self) -> dict:
        return json.loads(MEDIA_FIXTURE.read_text(encoding="utf-8"))

    def complete_measurements(self) -> dict:
        return {
            "width_px": 4096,
            "height_px": 4096,
            "alt_text_chars": 200,
            "color_profile": "sRGB",
            "target_sizes_px": [16, 32, 48],
            "monochrome_tested": True,
            "contrast_ratio": 7,
            "accessible_name_chars": 2,
            "lens_mm": 50,
            "edit_history_recorded": True,
            "placement_approved": True,
            "line_weight_mm": 0.5,
            "aging_reviewed": True,
            "consent_confirmed": True,
            "non_body_preview": True,
            "keyboard_accessible": True,
            "visible_focus": True,
            "reduced_motion": True,
            "non_color_meaning": True,
            "fallback_behavior": True,
            "duration_seconds": 30,
            "fps": 30,
            "captions_or_transcript": True,
            "pause_control": True,
            "flash_rate_hz": 0,
            "delivery_colorimetry": "BT.709",
            "scene_format": "GLB",
            "frame_start": 1,
            "frame_end": 30,
            "camera_defined": True,
            "lighting_defined": True,
            "units_defined": True,
            "render_settings_defined": True,
            "vector_format": "SVG",
            "viewbox_defined": True,
            "min_stroke_width_mm": 0.2,
            "fonts_recorded_or_outlined": True,
            "spot_colors_declared": True,
            "font_format": "OTF",
            "glyph_coverage_percent": 100,
            "font_license_recorded": True,
            "readability_tested": True,
            "text_version_chars": 100,
            "sample_rate_hz": 48000,
            "bit_depth_bits": 24,
            "channels": 2,
            "transcript_or_lyrics": True,
            "word_count": 100,
            "language": "en",
            "reading_level_measured": True,
            "text_versioned": True,
            "alternate_format_recorded": True,
            "page_count": 2,
            "panel_count": 8,
            "reading_order_declared": True,
            "text_layer_extractable": True,
            "transcript_or_alt_text": True,
            "cast_count": 2,
            "cue_sheet_recorded": True,
            "accessibility_plan_recorded": True,
            "venue_or_capture_plan_recorded": True,
            "consent_log_recorded": True,
            "build_id_chars": 8,
            "target_platform": "portable-web",
            "input_path_tested": True,
            "pause_behavior_tested": True,
            "save_state_tested": True,
            "render_mode": "2d",
            "runtime": "WebXR",
            "tracking_mode": "head-and-controller",
            "scale_units_defined": True,
            "comfort_review_recorded": True,
            "non_xr_fallback": True,
            "data_source_cited": True,
            "data_version_chars": 8,
            "legend_or_key_present": True,
            "numerical_precision_declared": True,
            "projection": "Equal Earth",
            "coordinate_reference_system_chars": 8,
            "scale_denominator": 10000,
            "scale_statement_recorded": True,
            "orientation_declared": True,
            "legend_present": True,
            "source_date_recorded": True,
            "material_chars": 8,
            "fabrication_method": "hand-built",
            "height_cm": 20,
            "width_cm": 30,
            "depth_cm": 5,
            "fabrication_plan_recorded": True,
            "material_disclosure": True,
            "handling_notes_recorded": True,
            "non_physical_preview": True,
            "trim_size_declared": True,
            "bleed_mm": 3,
            "pdf_standard": "PDF/X-4",
            "fonts_embedded_or_outlined": True,
            "preflight_run": True,
            "reading_order_tested": True,
            "real_content_tested": True,
            "source_count": 4,
            "source_ledger_recorded": True,
            "rights_status_recorded": True,
            "transformation_notes_recorded": True,
            "lossless_export_declared": True,
            "alpha_edges_tested": True,
            "frame_count": 8,
            "grid_declared": True,
            "nearest_neighbor_tested": True,
            "transparent_edges_tested": True,
            "actuator_profile": "test-device",
            "pattern_count": 2,
            "duration_ms": 400,
            "intensity_units": "device-relative",
            "safety_review_recorded": True,
            "non_haptic_alternative": True,
            "stop_control_tested": True,
            "venue_plan_recorded": True,
            "access_plan_recorded": True,
            "egress_reviewed": True,
            "load_reviewed": True,
            "hazard_reviewed": True,
            "removal_plan_recorded": True,
            "consent_scope_recorded": True,
            "attribution_policy_recorded": True,
            "data_minimized": True,
            "community_authority_recorded": True,
            "participant_count": 4,
            "withdrawal_path_recorded": True,
            "score_or_stems_recorded": True,
            "loudness_target_recorded": True,
            "listening_alternative_recorded": True,
        }

    def bundle_manifest(self) -> dict:
        base_case = deepcopy(self.load_fixture()["cases"][0])
        base_case["id"] = "mixed-artwork-bundle"
        base_case.pop("medium", None)
        base_case.pop("asset", None)
        base_case.pop("measurements", None)
        base_case["contract"] = deepcopy(self.load_contract_fixture()["cases"][0]["contract"])
        base_case["external_media"] = {"sources": [], "publisher_embeds": []}

        bundle_parts = [
            ("poster", "primary", "graphic_design", "vector_poster", "image/svg+xml"),
            ("sprites", "adjacent", "raster_vector_sprites", "pixel_sprite_sheet", "image/png"),
            ("haptics", "adjacent", "haptic", "haptic_pattern", "application/json"),
        ]
        requested = []
        delivered = []
        for part_id, role, medium, asset_type, format_name in bundle_parts:
            delivery = {"intended_use": "sample-gallery", "format": format_name}
            requested.append(
                {"id": part_id, "role": role, "medium": medium, "asset_type": asset_type, "delivery": delivery}
            )
            delivered.append(
                {
                    "id": part_id,
                    "role": role,
                    "medium": medium,
                    "asset": {
                        "label": part_id,
                        "type": asset_type,
                        "reference": "sample-source",
                        "path": f"package/{part_id}",
                    },
                    "measurements": self.complete_measurements(),
                    "delivery": deepcopy(delivery),
                }
            )
        base_case["representations"] = delivered
        request = {
            "schema_version": "1.0",
            "request_id": "sample-art-request",
            "version": "1",
            "operation": "generate",
            "intent": {"primary_effect": "show varied art routes", "meaning": "sample"},
            "subject_content": {},
            "art_direction": {},
            "representations": requested,
            "constraints": [{"text": "keep the route labels clear", "source": "user", "status": "required"}],
            "references": [],
            "people_and_authority": {},
            "audience_delivery": {},
            "accessibility_safety": {},
            "provenance": {},
            "open_questions": [],
            "review_handoff": {"owner": "sample-owner", "acceptance_tests": ["route and package check"]},
        }
        return {
            "manifest_id": "mixed-artwork-bundle",
            "schema_version": "1.3",
            "request": request,
            "cases": [base_case],
        }

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
        self.assertEqual(report["case_count"], 15)
        self.assertEqual(report["passed"], 15)
        self.assertEqual(report["held"], 0)
        self.assertEqual(report["contract_summary"]["constraints"], {"preserved": 17, "unmet": 1, "unknown": 0})
        self.assertEqual(report["contract_summary"]["capabilities"], {"required": 6, "satisfied": 6, "unmet": 0})
        self.assertEqual(report["contract_summary"]["descriptor_drift"], 1)
        self.assertEqual(report["contract_summary"]["descriptor_regressions"], 1)
        self.assertEqual(
            {case["canonical_medium"] for case in report["cases"]},
            {
                "illustration", "animation", "web", "raster_vector_sprites", "typography", "audio_haptic",
                "literary", "comics", "performance", "games", "xr", "data_visualization",
                "cartographic_art", "physical", "print",
            },
        )
        self.assertTrue(all(case["criteria_basis"] for case in report["cases"]))
        self.assertIn("soft_constraint_unmet", {warning["code"] for warning in report["cases"][0]["warnings"]})
        self.assertEqual(report["cases"][0]["contract"]["capabilities"]["adapters"][1]["status"], "adapted")

    def test_new_medium_aliases_resolve_to_registered_families(self) -> None:
        self.assertEqual(len(REPRESENTATION_ROWS), 24)
        self.assertEqual(len({row["standard_heading"] for row in REPRESENTATION_ROWS}), 24)
        for row in REPRESENTATION_ROWS:
            self.assertIn(row["id"], MEDIUM_CRITERIA)
            self.assertEqual(_resolve_medium(row["id"]), row["id"])
            for alias in row["aliases"]:
                self.assertEqual(_resolve_medium(alias), row["id"])
            for adjacent_route in row["adjacent_routes"]:
                self.assertIn(adjacent_route, MEDIUM_CRITERIA)
        self.assertEqual(_resolve_medium("logo"), "logos_icons")
        self.assertEqual(_resolve_medium("haptics"), "audio_haptic")
        self.assertEqual(_resolve_medium("pixel sprite sheet"), "raster_vector_sprites")

    def test_every_registry_route_passes_its_declared_check_profile(self) -> None:
        base_case = self.load_fixture()["cases"][0]
        cases = []
        for row in REPRESENTATION_ROWS:
            case = deepcopy(base_case)
            case["id"] = f"route-{row['id']}"
            case["medium"] = row["id"]
            case["asset"]["type"] = row["asset_types"][0]["id"]
            case["measurements"] = self.complete_measurements()
            cases.append(case)

        report = validate_manifest({"manifest_id": "all-representation-routes", "schema_version": "1.0", "cases": cases})
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["case_count"], 24)
        self.assertEqual(report["passed"], 24)
        self.assertEqual({case["canonical_medium"] for case in report["cases"]}, {row["id"] for row in REPRESENTATION_ROWS})
        self.assertTrue(all(case["criteria_basis"] for case in report["cases"]))

    def test_every_registered_asset_type_and_alias_passes_its_route_profiles(self) -> None:
        base_case = self.load_fixture()["cases"][0]
        cases = []
        for row in REPRESENTATION_ROWS:
            for type_index, declared_type in enumerate(row["asset_types"]):
                for asset_type in (declared_type["id"], *declared_type["aliases"]):
                    case = deepcopy(base_case)
                    case["id"] = f"{row['id']}-{type_index}-{asset_type}"
                    case["medium"] = row["id"]
                    case["asset"]["type"] = asset_type
                    case["measurements"] = self.complete_measurements()
                    cases.append(case)

        report = validate_manifest({"manifest_id": "all-registered-art-types", "schema_version": "1.0", "cases": cases})

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["case_count"], len(cases))
        self.assertTrue(all(case["criteria_basis"] for case in report["cases"]))

    def test_asset_type_is_checked_against_legacy_route(self) -> None:
        manifest = self.load_fixture()
        manifest["cases"][2]["asset"]["type"] = "vector"
        report = validate_manifest(manifest)
        photo_report = next(case for case in report["cases"] if case["id"] == "ethical-photo-scene")

        self.assertEqual(photo_report["status"], "hold")
        self.assertIn("asset_type_mismatch", {reason["code"] for reason in photo_report["reasons"]})

    def test_schema_13_validates_request_and_mixed_media_bundle(self) -> None:
        report = validate_manifest(self.bundle_manifest())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["schema_version"], "1.3")
        self.assertEqual(report["cases"][0]["status"], "pass")
        self.assertEqual(
            {item["route"] for item in report["cases"][0]["representations"]},
            {"graphic_design", "raster_vector_sprites", "audio_haptic"},
        )

    def test_schema_13_holds_when_request_and_bundle_drift(self) -> None:
        manifest = self.bundle_manifest()
        manifest["cases"][0]["representations"][1]["asset"]["type"] = "editorial_photo"
        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "hold")
        reasons = {reason["code"] for reason in report["cases"][0]["reasons"]}
        self.assertIn("asset_type_mismatch", reasons)
        self.assertIn("request_manifest_mismatch", reasons)

    def test_schema_13_holds_for_route_role_delivery_and_component_drift(self) -> None:
        mutations = (
            lambda manifest: manifest["cases"][0]["representations"][0].update(
                {"medium": "collage", "asset": {"label": "poster", "type": "collage_raster", "path": "package/poster"}}
            ),
            lambda manifest: manifest["cases"][0]["representations"][0].update({"role": "adjacent"}),
            lambda manifest: manifest["cases"][0]["representations"][0]["delivery"].update({"format": "image/png"}),
            lambda manifest: manifest["cases"][0]["representations"].pop(),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                manifest = self.bundle_manifest()
                mutate(manifest)
                report = validate_manifest(manifest)
                self.assertEqual(report["status"], "hold")
                self.assertIn(
                    "request_manifest_mismatch",
                    {reason["code"] for reason in report["cases"][0]["reasons"]},
                )

    def test_schema_13_request_requires_formal_contract_fields(self) -> None:
        manifest = self.bundle_manifest()
        manifest["request"].pop("audience_delivery")
        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "hold")
        self.assertIn("missing_value", {reason["code"] for reason in report["reasons"]})

    def test_schema_13_request_validates_optional_preserve_list_types(self) -> None:
        manifest = self.bundle_manifest()
        manifest["request"]["intent"]["preserve"] = [""]
        self.assertEqual(validate_manifest(manifest)["status"], "pass")

        manifest = self.bundle_manifest()
        manifest["request"]["intent"]["preserve"] = ["keep the primary subject", 7]

        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "hold")
        self.assertIn("invalid_type", {reason["code"] for reason in report["reasons"]})

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

    def test_invalid_capability_adapter_status_is_reported(self) -> None:
        manifest = self.load_contract_fixture()
        manifest["cases"][0]["contract"]["capabilities"]["adapters"]["image_generation"] = {"status": "native"}

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("invalid_value", codes)
        self.assertIn("capability_unmet", codes)
        self.assertEqual(result["contract"]["capabilities"]["adapters"][0]["status"], "native")

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

    def test_schema_12_portfolio_media_fixture_passes_declared_checks(self) -> None:
        report = validate_manifest(self.load_media_fixture())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["schema_version"], "1.2")
        self.assertEqual(report["case_count"], 1)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["cases"][0]["canonical_medium"], "web")
        self.assertIn("fetch or resolve assets or URLs", report["scope_note"])

    def test_factual_identification_status_passes_for_employer_mark(self) -> None:
        manifest = self.load_media_fixture()
        source = manifest["cases"][0]["external_media"]["sources"][0]

        self.assertEqual(source["kind"], "organization_mark")
        self.assertEqual(source["intended_usage_scope"], "organization_identification_only")
        self.assertEqual(source["usage_status"], "factual_identification")
        self.assertIn("Factual identification", source["usage_basis"])
        self.assertIn("identity-context", source["evidence_reference"])
        self.assertEqual(validate_manifest(manifest)["status"], "pass")

    def test_schema_12_requires_contract_and_external_media_declaration(self) -> None:
        manifest = self.load_fixture()
        manifest["schema_version"] = "1.2"

        report = validate_manifest(manifest)

        self.assertEqual(report["status"], "hold")
        for case in report["cases"]:
            self.assertIn(
                "missing_value",
                {reason["code"] for reason in case["reasons"]},
            )

    def test_external_source_requires_evidence_and_non_restricted_usage(self) -> None:
        for status in ("unknown", "restricted"):
            manifest = self.load_media_fixture()
            source = manifest["cases"][0]["external_media"]["sources"][0]
            source["usage_status"] = status
            source.pop("evidence_reference")

            result = validate_manifest(manifest)["cases"][0]
            codes = {reason["code"] for reason in result["reasons"]}

            self.assertEqual(result["status"], "hold")
            self.assertIn("external_source_hold", codes)
            self.assertIn("missing_value", codes)

    def test_external_source_scope_is_kind_specific_and_usage_basis_is_required(self) -> None:
        manifest = self.load_media_fixture()
        sources = manifest["cases"][0]["external_media"]["sources"]
        sources[0]["intended_usage_scope"] = "embed_only"
        sources[1].pop("usage_basis")

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("invalid_usage_scope", codes)
        self.assertIn("missing_value", codes)

    def test_factual_identification_status_is_restricted_to_mark_scope(self) -> None:
        mutations = (
            ("publisher_cinematic", "embed_only"),
            ("organization_mark", "embed_only"),
        )
        for kind, scope in mutations:
            manifest = self.load_media_fixture()
            source = manifest["cases"][0]["external_media"]["sources"][0]
            source["kind"] = kind
            source["intended_usage_scope"] = scope
            source["usage_status"] = "factual_identification"

            result = validate_manifest(manifest)["cases"][0]
            codes = {reason["code"] for reason in result["reasons"]}

            self.assertEqual(result["status"], "hold")
            self.assertIn("inapplicable_usage_status", codes)

    def test_publisher_cinematic_still_requires_permission_evidenced_status(self) -> None:
        manifest = self.load_media_fixture()
        publisher = manifest["cases"][0]["external_media"]["sources"][1]
        publisher["usage_status"] = "factual_identification"

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("inapplicable_usage_status", codes)
        self.assertIn("external_source_hold", codes)

    def test_publisher_embed_requires_a_matching_evidenced_source(self) -> None:
        manifest = self.load_media_fixture()
        embed = manifest["cases"][0]["external_media"]["publisher_embeds"][0]
        embed["source_id"] = "example-employer-mark"

        result = validate_manifest(manifest)["cases"][0]

        self.assertEqual(result["status"], "hold")
        self.assertIn("source_kind_mismatch", {reason["code"] for reason in result["reasons"]})

    def test_publisher_embed_rejects_unknown_status_and_unapproved_origins(self) -> None:
        manifest = self.load_media_fixture()
        embed = manifest["cases"][0]["external_media"]["publisher_embeds"][0]
        embed["embedding_status"] = "unknown"
        embed["provider"] = "vimeo"
        embed["origin"] = "http://www.youtube-nocookie.com"
        embed["csp_origins"] = ["https://unapproved.example.invalid"]

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("embed_hold", codes)
        self.assertIn("unapproved_provider", codes)
        self.assertIn("invalid_url", codes)
        self.assertIn("unapproved_origin", codes)

    def test_publisher_embed_denied_status_and_unapproved_profiles_hold(self) -> None:
        manifest = self.load_media_fixture()
        embed = manifest["cases"][0]["external_media"]["publisher_embeds"][0]
        embed["embedding_status"] = "denied"
        embed["sandbox_profile"] = "unreviewed-sandbox"
        embed["permissions_profile"] = "autoplay-enabled"
        embed["referrer_policy"] = "no-referrer"

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("embed_hold", codes)
        self.assertIn("unapproved_profile", codes)
        self.assertIn("invalid_referrer_policy", codes)

    def test_publisher_embedding_status_has_distinct_vocabulary(self) -> None:
        for status in ("permission_evidenced", "restricted"):
            manifest = self.load_media_fixture()
            embed = manifest["cases"][0]["external_media"]["publisher_embeds"][0]
            embed["embedding_status"] = status

            result = validate_manifest(manifest)["cases"][0]
            codes = {reason["code"] for reason in result["reasons"]}

            self.assertEqual(result["status"], "hold")
            self.assertIn("invalid_value", codes)
            self.assertNotIn("embed_hold", codes)

    def test_publisher_embed_rejects_autoplay_rehosting_download_and_inline_html(self) -> None:
        manifest = self.load_media_fixture()
        embed = manifest["cases"][0]["external_media"]["publisher_embeds"][0]
        embed["autoplay"] = True
        embed["downloaded"] = True
        embed["rehosted"] = True
        embed["click_to_load"] = False
        embed["iframe_html"] = '<iframe src="https://www.youtube.com/embed/A1B2C3D4E5F"></iframe>'

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("policy_violation", codes)
        self.assertIn("click_to_load_required", codes)
        self.assertIn("unsupported_field", codes)

    def test_publisher_embed_requires_alternatives_terms_and_canonical_fallback(self) -> None:
        manifest = self.load_media_fixture()
        embed = manifest["cases"][0]["external_media"]["publisher_embeds"][0]
        embed.pop("transcript_reference")
        embed.pop("terms_checked_on")
        embed["fallback_url"] = "https://www.youtube.com/watch?v=OtherVideo01"

        result = validate_manifest(manifest)["cases"][0]
        codes = {reason["code"] for reason in result["reasons"]}

        self.assertEqual(result["status"], "hold")
        self.assertIn("missing_value", codes)
        self.assertIn("invalid_fallback", codes)

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
