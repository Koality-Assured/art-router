"""Validate art-router next-steps case manifests without external services.

tags: [validation, art-router, scripts]
routing_hints: [manifest, fixtures, provenance, accessibility, delivery, review]

The validator checks declared controls and supplied measurements. It deliberately
does not open asset paths, make network calls, or claim that metadata proves
artistic quality, rights, safety, or accessibility in the real world.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable


MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_CASES = 1000
MAX_TEXT_LENGTH = 10_000

MEDIUM_ALIASES = {
    "2d": "illustration",
    "body_art": "tattoo",
    "cgi_3d": "cgi",
    "favicon": "icon",
    "graphic_mark": "icon",
    "icons": "icon",
    "interactive_web": "web",
    "motion": "animation",
    "painting": "illustration",
    "photo": "photography",
    "three_d": "cgi",
    "video": "animation",
}


class Issue:
    """One deterministic validation reason."""

    __slots__ = ("code", "message")

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def _issue(issues: list[Issue], code: str, message: str) -> None:
    issues.append(Issue(code, message))


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _text(
    value: Any,
    field: str,
    issues: list[Issue],
    *,
    required: bool = True,
) -> str | None:
    if value is None:
        if required:
            _issue(issues, "missing_value", f"{field} must be provided")
        return None
    if not isinstance(value, str):
        if required:
            _issue(issues, "invalid_type", f"{field} must be a string")
        return None
    stripped = value.strip()
    if required and not stripped:
        _issue(issues, "missing_value", f"{field} must not be empty")
    if len(value) > MAX_TEXT_LENGTH:
        _issue(issues, "text_too_long", f"{field} exceeds {MAX_TEXT_LENGTH} characters")
    return stripped


def _mapping(value: Any, field: str, issues: list[Issue]) -> dict[str, Any] | None:
    if not _is_mapping(value):
        _issue(issues, "invalid_type", f"{field} must be an object")
        return None
    return value


def _list(value: Any, field: str, issues: list[Issue]) -> list[Any] | None:
    if not isinstance(value, list):
        _issue(issues, "invalid_type", f"{field} must be an array")
        return None
    return value


def _nonempty_string_list(value: Any, field: str, issues: list[Issue]) -> list[str] | None:
    values = _list(value, field, issues)
    if values is None:
        return None
    if not values:
        _issue(issues, "missing_value", f"{field} must not be empty")
    result: list[str] = []
    for index, item in enumerate(values):
        parsed = _text(item, f"{field}[{index}]", issues)
        if parsed is not None:
            result.append(parsed)
    return result


def _finite_number(value: Any, field: str, issues: list[Issue]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _issue(issues, "invalid_type", f"{field} must be a finite number")
        return None
    if not math.isfinite(float(value)):
        _issue(issues, "invalid_value", f"{field} must be finite")
        return None
    return float(value)


def _required_bool(value: Any, field: str, issues: list[Issue]) -> bool | None:
    if not isinstance(value, bool):
        _issue(issues, "invalid_type", f"{field} must be boolean")
        return None
    if not value:
        _issue(issues, "criterion_failed", f"{field} must be true")
    return value


def _check_int_list_contains(
    measurements: dict[str, Any],
    field: str,
    required: set[int],
    issues: list[Issue],
) -> None:
    values = measurements.get(field)
    if not isinstance(values, list):
        _issue(issues, "invalid_type", f"measurements.{field} must be an array")
        return
    actual: set[int] = set()
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, int):
            _issue(issues, "invalid_type", f"measurements.{field}[{index}] must be an integer")
        else:
            actual.add(value)
    missing = sorted(required - actual)
    if missing:
        _issue(issues, "criterion_failed", f"measurements.{field} is missing sizes: {missing}")


def _check_min_number(
    measurements: dict[str, Any], field: str, minimum: float, issues: list[Issue]
) -> None:
    value = _finite_number(measurements.get(field), f"measurements.{field}", issues)
    if value is not None and value < minimum:
        _issue(issues, "criterion_failed", f"measurements.{field} must be at least {minimum:g}")


def _check_positive_number(measurements: dict[str, Any], field: str, issues: list[Issue]) -> None:
    value = _finite_number(measurements.get(field), f"measurements.{field}", issues)
    if value is not None and value <= 0:
        _issue(issues, "criterion_failed", f"measurements.{field} must be greater than 0")


def _check_text_min(measurements: dict[str, Any], field: str, minimum: int, issues: list[Issue]) -> None:
    value = measurements.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        _issue(issues, "invalid_type", f"measurements.{field} must be an integer")
    elif value < minimum:
        _issue(issues, "criterion_failed", f"measurements.{field} must be at least {minimum}")


def _check_allowed_text(
    measurements: dict[str, Any], field: str, allowed: set[str], issues: list[Issue]
) -> None:
    value = _text(measurements.get(field), f"measurements.{field}", issues)
    if value is not None and value.lower() not in {item.lower() for item in allowed}:
        _issue(issues, "criterion_failed", f"measurements.{field} must be one of {sorted(allowed)}")


def _check_bool(measurements: dict[str, Any], field: str, issues: list[Issue]) -> None:
    _required_bool(measurements.get(field), f"measurements.{field}", issues)


def _check_frame_range(measurements: dict[str, Any], issues: list[Issue]) -> None:
    start = measurements.get("frame_start")
    end = measurements.get("frame_end")
    if isinstance(start, bool) or not isinstance(start, int):
        _issue(issues, "invalid_type", "measurements.frame_start must be an integer")
    if isinstance(end, bool) or not isinstance(end, int):
        _issue(issues, "invalid_type", "measurements.frame_end must be an integer")
    if isinstance(start, int) and not isinstance(start, bool) and isinstance(end, int) and not isinstance(end, bool):
        if end < start:
            _issue(issues, "criterion_failed", "measurements.frame_end must be at least frame_start")


CriterionCheck = Callable[[dict[str, Any], list[Issue]], None]


MEDIUM_CRITERIA: dict[str, tuple[str, CriterionCheck]] = {
    "illustration": (
        "delivery-size, equivalent-description, and color-profile declarations",
        lambda m, i: (
            _check_min_number(m, "width_px", 1024, i),
            _check_min_number(m, "height_px", 1024, i),
            _check_text_min(m, "alt_text_chars", 40, i),
            _check_allowed_text(m, "color_profile", {"sRGB", "Display-P3", "Adobe RGB"}, i),
        ),
    ),
    "icon": (
        "small-size exports, monochrome behavior, and non-color contrast",
        lambda m, i: (
            _check_int_list_contains(m, "target_sizes_px", {16, 32, 48}, i),
            _check_bool(m, "monochrome_tested", i),
            _check_min_number(m, "contrast_ratio", 3, i),
            _check_text_min(m, "accessible_name_chars", 1, i),
        ),
    ),
    "photography": (
        "capture scale, lens declaration, equivalent description, and edit history",
        lambda m, i: (
            _check_min_number(m, "width_px", 2000, i),
            _check_min_number(m, "height_px", 1500, i),
            _check_positive_number(m, "lens_mm", i),
            _check_text_min(m, "alt_text_chars", 40, i),
            _check_bool(m, "edit_history_recorded", i),
        ),
    ),
    "tattoo": (
        "placement, line-weight, aging, informed consent, and non-body preview",
        lambda m, i: (
            _check_bool(m, "placement_approved", i),
            _check_positive_number(m, "line_weight_mm", i),
            _check_bool(m, "aging_reviewed", i),
            _check_bool(m, "consent_confirmed", i),
            _check_bool(m, "non_body_preview", i),
        ),
    ),
    "web": (
        "keyboard path, focus, reduced motion, contrast, non-color meaning, and fallback",
        lambda m, i: (
            _check_bool(m, "keyboard_accessible", i),
            _check_bool(m, "visible_focus", i),
            _check_bool(m, "reduced_motion", i),
            _check_min_number(m, "contrast_ratio", 4.5, i),
            _check_bool(m, "non_color_meaning", i),
            _check_bool(m, "fallback_behavior", i),
        ),
    ),
    "animation": (
        "duration, frame rate, time-based alternatives, pause control, flashing, and colorimetry",
        lambda m, i: (
            _check_positive_number(m, "duration_seconds", i),
            _check_fps_number(m, i),
            _check_bool(m, "captions_or_transcript", i),
            _check_bool(m, "pause_control", i),
            _check_flash_rate(m, i),
            _check_allowed_text(m, "delivery_colorimetry", {"BT.709", "BT.2100"}, i),
        ),
    ),
    "cgi": (
        "scene format, frame range, frame rate, camera, lighting, units, and render settings",
        lambda m, i: (
            _check_allowed_text(m, "scene_format", {"USD", "USDZ", "glTF", "GLB"}, i),
            _check_frame_range(m, i),
            _check_positive_number(m, "fps", i),
            _check_bool(m, "camera_defined", i),
            _check_bool(m, "lighting_defined", i),
            _check_bool(m, "units_defined", i),
            _check_bool(m, "render_settings_defined", i),
        ),
    ),
}


def _check_fps_number(measurements: dict[str, Any], issues: list[Issue]) -> None:
    value = _finite_number(measurements.get("fps"), "measurements.fps", issues)
    if value is not None and value not in {24, 25, 30, 48, 50, 60}:
        _issue(issues, "criterion_failed", "measurements.fps must be one of 24, 25, 30, 48, 50, or 60")


def _check_flash_rate(measurements: dict[str, Any], issues: list[Issue]) -> None:
    value = _finite_number(measurements.get("flash_rate_hz"), "measurements.flash_rate_hz", issues)
    if value is not None and (value < 0 or value > 3):
        _issue(issues, "criterion_failed", "measurements.flash_rate_hz must be between 0 and 3")


def _validate_controls(case: dict[str, Any], issues: list[Issue]) -> None:
    intent = _mapping(case.get("intent"), "intent", issues)
    if intent is not None:
        for field in ("statement", "audience", "context"):
            _text(intent.get(field), f"intent.{field}", issues)

    provenance = _mapping(case.get("provenance"), "provenance", issues)
    if provenance is not None:
        sources = _list(provenance.get("sources"), "provenance.sources", issues)
        if sources is not None:
            if not sources:
                _issue(issues, "missing_value", "provenance.sources must not be empty")
            for index, source in enumerate(sources):
                source_map = _mapping(source, f"provenance.sources[{index}]", issues)
                if source_map is not None:
                    _text(source_map.get("reference"), f"provenance.sources[{index}].reference", issues)
                    _text(source_map.get("rights"), f"provenance.sources[{index}].rights", issues)
        rights_status = _text(provenance.get("rights_status"), "provenance.rights_status", issues)
        if rights_status is not None:
            normalized_rights_status = rights_status.lower()
            allowed_rights_statuses = {
                "cleared",
                "licensed",
                "original",
                "public_domain",
                "unknown",
                "restricted",
            }
            if normalized_rights_status not in allowed_rights_statuses:
                _issue(issues, "invalid_value", "provenance.rights_status is not a recognized status")
            elif normalized_rights_status in {"unknown", "restricted"}:
                _issue(issues, "rights_hold", "provenance.rights_status does not authorize delivery")
        _text(provenance.get("rights_basis"), "provenance.rights_basis", issues)
        _text(provenance.get("human_authorship"), "provenance.human_authorship", issues)
        _text(provenance.get("tool_use"), "provenance.tool_use", issues)

    checks = _mapping(case.get("checks"), "checks", issues)
    if checks is not None:
        for check_name in ("cultural", "safety", "accessibility"):
            check = _mapping(checks.get(check_name), f"checks.{check_name}", issues)
            if check is None:
                continue
            status = _text(check.get("status"), f"checks.{check_name}.status", issues)
            if status is not None and status.lower() not in {"pass", "not_applicable", "hold"}:
                _issue(issues, "invalid_value", f"checks.{check_name}.status must be pass, not_applicable, or hold")
            if status is not None and status.lower() == "hold":
                _issue(issues, "declared_check_hold", f"checks.{check_name} is declared hold")
            _text(check.get("notes"), f"checks.{check_name}.notes", issues)

    delivery = _mapping(case.get("delivery"), "delivery", issues)
    if delivery is not None:
        _nonempty_string_list(delivery.get("formats"), "delivery.formats", issues)
        _nonempty_string_list(delivery.get("targets"), "delivery.targets", issues)
        metadata = _mapping(delivery.get("metadata"), "delivery.metadata", issues)
        if metadata is not None:
            for field in ("owner", "version", "fallback_or_limitation"):
                _text(metadata.get(field), f"delivery.metadata.{field}", issues)
        complete = delivery.get("metadata_complete")
        if complete is not True:
            _issue(issues, "delivery_hold", "delivery.metadata_complete must be true")

    reviewer = _mapping(case.get("reviewer"), "reviewer", issues)
    if reviewer is not None:
        decision = _text(reviewer.get("decision"), "reviewer.decision", issues)
        if decision is not None and decision.lower() not in {"approve", "hold", "reject"}:
            _issue(issues, "invalid_value", "reviewer.decision must be approve, hold, or reject")
        if decision is not None and decision.lower() in {"hold", "reject"}:
            _issue(issues, "review_hold", f"reviewer.decision is {decision.lower()}")
        _text(reviewer.get("reviewer_id"), "reviewer.reviewer_id", issues)
        _text(reviewer.get("observations"), "reviewer.observations", issues)
        _text(reviewer.get("reviewed_at"), "reviewer.reviewed_at", issues)


def _validate_case(case: Any, index: int) -> dict[str, Any]:
    issues: list[Issue] = []
    if not _is_mapping(case):
        _issue(issues, "invalid_type", f"case[{index}] must be an object")
        return {
            "id": f"case[{index}]",
            "medium": None,
            "status": "hold",
            "reasons": [issue.as_dict() for issue in issues],
            "criteria_basis": None,
        }

    case_id = _text(case.get("id"), f"case[{index}].id", issues) or f"case[{index}]"
    medium_input = _text(case.get("medium"), f"case[{index}].medium", issues)
    canonical_medium = MEDIUM_ALIASES.get(medium_input.lower(), medium_input.lower()) if medium_input else None
    if canonical_medium not in MEDIUM_CRITERIA:
        _issue(
            issues,
            "unsupported_medium",
            f"case {_safe_display(case_id)} uses unsupported medium {_safe_display(medium_input)!r}",
        )

    asset = case.get("asset")
    if asset is not None:
        asset_map = _mapping(asset, f"case[{index}].asset", issues)
        if asset_map is not None:
            _text(asset_map.get("label"), f"case[{index}].asset.label", issues)
            _text(asset_map.get("type"), f"case[{index}].asset.type", issues)
            # `reference` is informational only; it is never opened or resolved.
            _text(asset_map.get("reference"), f"case[{index}].asset.reference", issues)

    _validate_controls(case, issues)

    criteria_basis: str | None = None
    measurements = case.get("measurements")
    if canonical_medium in MEDIUM_CRITERIA:
        criteria_basis, criterion_check = MEDIUM_CRITERIA[canonical_medium]
        measurement_map = _mapping(measurements, "measurements", issues)
        if measurement_map is not None:
            criterion_check(measurement_map, issues)
    elif measurements is not None:
        _mapping(measurements, "measurements", issues)

    return {
        "id": case_id,
        "medium": medium_input,
        "canonical_medium": canonical_medium,
        "status": "pass" if not issues else "hold",
        "reasons": [issue.as_dict() for issue in issues],
        "criteria_basis": criteria_basis,
    }


def validate_manifest(data: Any) -> dict[str, Any]:
    """Return a deterministic pass/hold report for untrusted decoded JSON."""
    report: dict[str, Any] = {
        "status": "hold",
        "manifest_id": None,
        "case_count": 0,
        "passed": 0,
        "held": 0,
        "reasons": [],
        "cases": [],
        "scope_note": (
            "Validates declared controls and supplied measurements only; it does not "
            "prove artistic quality, rights, safety, accessibility, or asset existence."
        ),
    }
    manifest_issues: list[Issue] = []
    if not _is_mapping(data):
        _issue(manifest_issues, "invalid_type", "manifest must be a JSON object")
        report["reasons"] = [issue.as_dict() for issue in manifest_issues]
        return report

    manifest_id = _text(data.get("manifest_id"), "manifest_id", manifest_issues)
    report["manifest_id"] = manifest_id
    schema_version = _text(data.get("schema_version"), "schema_version", manifest_issues)
    if schema_version != "1.0":
        _issue(manifest_issues, "unsupported_schema", "schema_version must be '1.0'")

    cases = _list(data.get("cases"), "cases", manifest_issues)
    if cases is not None:
        if not cases:
            _issue(manifest_issues, "missing_value", "cases must contain at least one case")
        if len(cases) > MAX_CASES:
            _issue(manifest_issues, "too_many_cases", f"cases must contain at most {MAX_CASES} cases")
        seen_ids: set[str] = set()
        for index, case in enumerate(cases[:MAX_CASES]):
            result = _validate_case(case, index)
            if result["id"] in seen_ids:
                result["reasons"].append({"code": "duplicate_id", "message": f"duplicate case id {result['id']!r}"})
                result["status"] = "hold"
            seen_ids.add(result["id"])
            report["cases"].append(result)

    report["case_count"] = len(report["cases"])
    report["passed"] = sum(result["status"] == "pass" for result in report["cases"])
    report["held"] = sum(result["status"] == "hold" for result in report["cases"])
    report["reasons"] = [issue.as_dict() for issue in manifest_issues]
    if not manifest_issues and report["held"] == 0 and report["case_count"] > 0:
        report["status"] = "pass"
    return report


def _load_manifest(path: Path) -> Any:
    raw = path.read_bytes()
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("manifest must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc


def _safe_display(value: Any) -> str:
    """Keep untrusted ids from emitting terminal control characters in text mode."""
    return str(value).replace("\r", "\\r").replace("\n", "\\n").replace("\x1b", "\\x1b")


def _text_report(report: dict[str, Any]) -> str:
    lines = [
        f"manifest: {_safe_display(report['manifest_id'])}",
        f"status: {report['status']}",
        f"cases: {report['case_count']} (pass={report['passed']}, hold={report['held']})",
    ]
    for reason in report["reasons"]:
        lines.append(f"manifest hold [{reason['code']}]: {reason['message']}")
    for case in report["cases"]:
        lines.append(
            f"- {_safe_display(case['id'])} ({_safe_display(case['medium'])}): {case['status']}"
        )
        for reason in case["reasons"]:
            lines.append(f"  - [{reason['code']}] {reason['message']}")
    lines.append(f"scope: {report['scope_note']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a deterministic art-router case manifest without external services."
    )
    parser.add_argument("--manifest", required=True, type=Path, help="UTF-8 JSON manifest to validate")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit the structured report as JSON")
    parser.add_argument("--fail-on-hold", action="store_true", help="return exit code 1 when any hold is reported")
    args = parser.parse_args(argv)

    try:
        data = _load_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2

    report = validate_manifest(data)
    if args.as_json:
        print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
    else:
        print(_text_report(report))
    return 1 if args.fail_on_hold and report["status"] == "hold" else 0


if __name__ == "__main__":
    raise SystemExit(main())
