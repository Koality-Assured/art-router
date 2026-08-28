"""Validate art-router next-steps case manifests without external services.

tags: [validation, art-router, scripts]
routing_hints: [manifest, fixtures, provenance, accessibility, delivery, review, request-contract]

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
MAX_CONTRACT_ITEMS = 100
MAX_DESCRIPTOR_KEYS = 100

CONTRACT_HARDNESS = {"hard", "soft"}
CONTRACT_COMPARISONS = {"exact", "contains", "at_least", "at_most"}
CAPABILITY_STATUSES = {"available", "adapted", "unavailable", "unknown", "unreported"}
RESOLVED_STATES = {"resolved", "closed", "not_applicable"}

MEDIUM_ALIASES = {
    "2d": "illustration",
    "ar": "xr",
    "body_art": "tattoo",
    "cgi_3d": "cgi",
    "cartography": "cartographic_art",
    "data_viz": "data_visualization",
    "dance": "performance",
    "extended_reality": "xr",
    "favicon": "icon",
    "graphic_mark": "icon",
    "graphic_novel": "comics",
    "game": "games",
    "icons": "icon",
    "interactive_web": "web",
    "information_visualization": "data_visualization",
    "installation": "physical",
    "lettering": "typography",
    "live_performance": "performance",
    "logo": "vector",
    "map_art": "cartographic_art",
    "mapping": "cartographic_art",
    "material_fabrication": "physical",
    "mixed_reality": "xr",
    "motion": "animation",
    "music": "audio",
    "painting": "illustration",
    "packaging": "print",
    "photo": "photography",
    "poetry": "literary",
    "print_design": "print",
    "prose": "literary",
    "publication": "print",
    "sculpture": "physical",
    "sequential_art": "comics",
    "software_art": "games",
    "sound": "audio",
    "storyboard": "comics",
    "text": "literary",
    "theatre": "performance",
    "three_d": "cgi",
    "video": "animation",
    "voice": "audio",
    "vr": "xr",
    "writing": "literary",
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


def _warning(warnings: list[Issue], code: str, message: str) -> None:
    warnings.append(Issue(code, message))


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _normalize_token(value: str) -> str:
    """Normalize provider-specific identifier spelling for contract comparisons."""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


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


def _check_declared_text(measurements: dict[str, Any], field: str, issues: list[Issue]) -> None:
    _text(measurements.get(field), f"measurements.{field}", issues)


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


def _check_positive_integer(measurements: dict[str, Any], field: str, issues: list[Issue]) -> None:
    value = measurements.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        _issue(issues, "invalid_type", f"measurements.{field} must be an integer")
    elif value <= 0:
        _issue(issues, "criterion_failed", f"measurements.{field} must be greater than 0")


def _check_nonnegative_number(measurements: dict[str, Any], field: str, issues: list[Issue]) -> None:
    value = _finite_number(measurements.get(field), f"measurements.{field}", issues)
    if value is not None and value < 0:
        _issue(issues, "criterion_failed", f"measurements.{field} must be non-negative")


def _check_allowed_number(
    measurements: dict[str, Any], field: str, allowed: set[float], issues: list[Issue]
) -> None:
    value = _finite_number(measurements.get(field), f"measurements.{field}", issues)
    if value is not None and value not in allowed:
        _issue(issues, "criterion_failed", f"measurements.{field} must be one of {sorted(allowed)}")


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
    "vector": (
        "non-empty vector-format, viewBox, stroke, font, and spot-color declarations",
        lambda m, i: (
            _check_declared_text(m, "vector_format", i),
            _check_bool(m, "viewbox_defined", i),
            _check_positive_number(m, "min_stroke_width_mm", i),
            _check_bool(m, "fonts_recorded_or_outlined", i),
            _check_bool(m, "spot_colors_declared", i),
        ),
    ),
    "typography": (
        "non-empty font-format, glyph coverage, licensing, readability, and text-layer declarations",
        lambda m, i: (
            _check_declared_text(m, "font_format", i),
            _check_min_number(m, "glyph_coverage_percent", 95, i),
            _check_bool(m, "font_license_recorded", i),
            _check_bool(m, "readability_tested", i),
            _check_text_min(m, "text_version_chars", 1, i),
        ),
    ),
    "audio": (
        "duration, sample rate, bit depth, channel count, and transcript-or-lyrics declarations",
        lambda m, i: (
            _check_positive_number(m, "duration_seconds", i),
            _check_allowed_number(m, "sample_rate_hz", {44100, 48000, 96000}, i),
            _check_positive_integer(m, "bit_depth_bits", i),
            _check_positive_integer(m, "channels", i),
            _check_bool(m, "transcript_or_lyrics", i),
        ),
    ),
    "literary": (
        "word count, non-empty language, reading-level, version, and alternate-format declarations",
        lambda m, i: (
            _check_positive_integer(m, "word_count", i),
            _check_declared_text(m, "language", i),
            _check_bool(m, "reading_level_measured", i),
            _check_bool(m, "text_versioned", i),
            _check_bool(m, "alternate_format_recorded", i),
        ),
    ),
    "comics": (
        "page and panel counts, reading order, extractable text, equivalent description, and color profile",
        lambda m, i: (
            _check_positive_integer(m, "page_count", i),
            _check_positive_integer(m, "panel_count", i),
            _check_bool(m, "reading_order_declared", i),
            _check_bool(m, "text_layer_extractable", i),
            _check_bool(m, "transcript_or_alt_text", i),
            _check_declared_text(m, "color_profile", i),
        ),
    ),
    "performance": (
        "duration, cast count, cue sheet, access plan, and venue-or-capture declarations",
        lambda m, i: (
            _check_positive_number(m, "duration_seconds", i),
            _check_positive_integer(m, "cast_count", i),
            _check_bool(m, "cue_sheet_recorded", i),
            _check_bool(m, "accessibility_plan_recorded", i),
            _check_bool(m, "venue_or_capture_plan_recorded", i),
            _check_bool(m, "consent_log_recorded", i),
        ),
    ),
    "games": (
        "build identity, non-empty platform, input, pause, save-state, and render-mode declarations",
        lambda m, i: (
            _check_text_min(m, "build_id_chars", 1, i),
            _check_declared_text(m, "target_platform", i),
            _check_bool(m, "input_path_tested", i),
            _check_bool(m, "pause_behavior_tested", i),
            _check_bool(m, "save_state_tested", i),
            _check_declared_text(m, "render_mode", i),
        ),
    ),
    "xr": (
        "non-empty runtime and tracking declarations, frame rate, scale units, comfort review, and non-XR fallback",
        lambda m, i: (
            _check_declared_text(m, "runtime", i),
            _check_declared_text(m, "tracking_mode", i),
            _check_fps_number(m, i),
            _check_bool(m, "scale_units_defined", i),
            _check_bool(m, "comfort_review_recorded", i),
            _check_bool(m, "non_xr_fallback", i),
        ),
    ),
    "data_visualization": (
        "data source, version, units, legend, non-color encoding, precision, and text alternative declarations",
        lambda m, i: (
            _check_bool(m, "data_source_cited", i),
            _check_text_min(m, "data_version_chars", 1, i),
            _check_bool(m, "units_defined", i),
            _check_bool(m, "legend_or_key_present", i),
            _check_bool(m, "non_color_meaning", i),
            _check_bool(m, "numerical_precision_declared", i),
            _check_text_min(m, "alt_text_chars", 40, i),
        ),
    ),
    "cartographic_art": (
        "non-empty projection, coordinate reference, scale, orientation, legend, and source-date declarations",
        lambda m, i: (
            _check_declared_text(m, "projection", i),
            _check_text_min(m, "coordinate_reference_system_chars", 1, i),
            _check_positive_number(m, "scale_denominator", i),
            _check_bool(m, "scale_statement_recorded", i),
            _check_bool(m, "orientation_declared", i),
            _check_bool(m, "legend_present", i),
            _check_bool(m, "source_date_recorded", i),
        ),
    ),
    "physical": (
        "material, dimensions, non-empty fabrication method, handling notes, and non-physical preview declarations",
        lambda m, i: (
            _check_text_min(m, "material_chars", 1, i),
            _check_declared_text(m, "fabrication_method", i),
            _check_positive_number(m, "height_cm", i),
            _check_positive_number(m, "width_cm", i),
            _check_positive_number(m, "depth_cm", i),
            _check_bool(m, "fabrication_plan_recorded", i),
            _check_bool(m, "material_disclosure", i),
            _check_bool(m, "handling_notes_recorded", i),
            _check_bool(m, "non_physical_preview", i),
        ),
    ),
    "print": (
        "page count, trim and bleed, non-empty color profile and PDF standard, font handling, and preflight declarations",
        lambda m, i: (
            _check_positive_integer(m, "page_count", i),
            _check_bool(m, "trim_size_declared", i),
            _check_nonnegative_number(m, "bleed_mm", i),
            _check_declared_text(m, "color_profile", i),
            _check_declared_text(m, "pdf_standard", i),
            _check_bool(m, "fonts_embedded_or_outlined", i),
            _check_bool(m, "preflight_run", i),
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


def _empty_contract_report(*, present: bool = False) -> dict[str, Any]:
    return {
        "present": present,
        "constraints": [],
        "preserved": 0,
        "unmet": 0,
        "unknown": 0,
        "ambiguities": [],
        "conflicts": [],
        "capabilities": {
            "required": [],
            "adapters": [],
            "satisfied": [],
            "unmet": [],
        },
        "descriptors": {
            "requested": {},
            "delivered": {},
            "drift": [],
            "regressions": [],
            "added": [],
        },
    }


def _canonical_descriptor_map(
    value: Any, field: str, issues: list[Issue]
) -> dict[str, Any] | None:
    parsed = _mapping(value, field, issues)
    if parsed is None:
        return None
    if len(parsed) > MAX_DESCRIPTOR_KEYS:
        _issue(issues, "too_many_items", f"{field} must contain at most {MAX_DESCRIPTOR_KEYS} keys")
    result: dict[str, Any] = {}
    for raw_key, item in parsed.items():
        if not isinstance(raw_key, str) or not raw_key.strip():
            _issue(issues, "invalid_value", f"{field} keys must be non-empty strings")
            continue
        key = _normalize_token(raw_key)
        if key in result:
            _issue(issues, "invalid_value", f"{field} contains duplicate normalized key {key!r}")
            continue
        result[key] = item
    return result


def _canonical_key_list(value: Any, field: str, issues: list[Issue]) -> set[str]:
    values = _list(value, field, issues)
    if values is None:
        return set()
    if len(values) > MAX_DESCRIPTOR_KEYS:
        _issue(issues, "too_many_items", f"{field} must contain at most {MAX_DESCRIPTOR_KEYS} items")
    result: set[str] = set()
    for index, item in enumerate(values):
        parsed = _text(item, f"{field}[{index}]", issues)
        if parsed is not None:
            result.add(_normalize_token(parsed))
    return result


def _compare_contract_values(requested: Any, delivered: Any, comparison: str) -> bool | None:
    if comparison == "exact":
        return requested == delivered
    if comparison == "contains":
        if isinstance(requested, str) and isinstance(delivered, str):
            return requested in delivered
        if isinstance(requested, list) and isinstance(delivered, list):
            return all(item in delivered for item in requested)
        if isinstance(requested, dict) and isinstance(delivered, dict):
            return all(key in delivered and delivered[key] == item for key, item in requested.items())
        return None
    if comparison in {"at_least", "at_most"}:
        if (
            isinstance(requested, bool)
            or isinstance(delivered, bool)
            or not isinstance(requested, (int, float))
            or not isinstance(delivered, (int, float))
            or not math.isfinite(float(requested))
            or not math.isfinite(float(delivered))
        ):
            return None
        return delivered >= requested if comparison == "at_least" else delivered <= requested
    return None


def _validate_status_items(
    contract: dict[str, Any],
    field: str,
    issues: list[Issue],
    report_items: list[dict[str, Any]],
) -> None:
    values = contract.get(field, [])
    parsed_values = _list(values, f"contract.{field}", issues)
    if parsed_values is None:
        return
    if len(parsed_values) > MAX_CONTRACT_ITEMS:
        _issue(issues, "too_many_items", f"contract.{field} must contain at most {MAX_CONTRACT_ITEMS} items")
    seen: set[str] = set()
    hold_code = {"ambiguities": "ambiguity_hold", "conflicts": "conflict_hold"}[field]
    for index, item in enumerate(parsed_values[:MAX_CONTRACT_ITEMS]):
        item_map = _mapping(item, f"contract.{field}[{index}]", issues)
        if item_map is None:
            continue
        item_id = _text(item_map.get("id"), f"contract.{field}[{index}].id", issues)
        description = _text(
            item_map.get("description"), f"contract.{field}[{index}].description", issues
        )
        status = _text(item_map.get("status"), f"contract.{field}[{index}].status", issues)
        normalized_status = _normalize_token(status) if status else None
        if item_id is not None:
            normalized_id = _normalize_token(item_id)
            if normalized_id in seen:
                _issue(issues, "duplicate_id", f"duplicate contract.{field} id {item_id!r}")
            seen.add(normalized_id)
        if normalized_status is not None and normalized_status not in {
            "open",
            "unresolved",
            "resolved",
            "closed",
            "not_applicable",
        }:
            _issue(issues, "invalid_value", f"contract.{field}[{index}].status is not recognized")
        if normalized_status not in RESOLVED_STATES:
            _issue(issues, hold_code, f"contract.{field}[{index}] is not resolved")
        report_items.append(
            {
                "id": item_id,
                "description": description,
                "status": normalized_status,
                "resolution": _text(
                    item_map.get("resolution"),
                    f"contract.{field}[{index}].resolution",
                    issues,
                    required=False,
                ),
            }
        )


def _validate_capabilities(
    contract: dict[str, Any], issues: list[Issue], report: dict[str, Any]
) -> None:
    capabilities = contract.get("capabilities")
    if capabilities is None:
        return
    capability_map = _mapping(capabilities, "contract.capabilities", issues)
    if capability_map is None:
        return
    required = _list(capability_map.get("required"), "contract.capabilities.required", issues)
    if required is None:
        return
    if len(required) > MAX_CONTRACT_ITEMS:
        _issue(issues, "too_many_items", f"contract.capabilities.required must contain at most {MAX_CONTRACT_ITEMS} items")
    required_tokens: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(required[:MAX_CONTRACT_ITEMS]):
        parsed = _text(item, f"contract.capabilities.required[{index}]", issues)
        if parsed is None:
            continue
        token = _normalize_token(parsed)
        if token in seen:
            _issue(issues, "duplicate_id", f"duplicate required capability {parsed!r}")
        else:
            seen.add(token)
            required_tokens.append(token)

    adapters = capability_map.get("adapters", {})
    if not isinstance(adapters, (dict, list)):
        _issue(issues, "invalid_type", "contract.capabilities.adapters must be an object or array")
        adapters = {}
    adapter_records: dict[str, dict[str, Any]] = {}
    if isinstance(adapters, dict):
        adapter_items = sorted(adapters.items(), key=lambda item: str(item[0]))
        for raw_name, raw_status in adapter_items:
            if not isinstance(raw_name, str) or not raw_name.strip():
                _issue(issues, "invalid_value", "contract.capabilities.adapters keys must be non-empty strings")
                continue
            token = _normalize_token(raw_name)
            if isinstance(raw_status, dict):
                status_value = raw_status.get("status")
                adapter_name = raw_status.get("adapter", raw_status.get("name"))
            else:
                status_value = raw_status
                adapter_name = None
            status = _text(status_value, f"contract.capabilities.adapters.{raw_name}.status", issues)
            adapter = _text(
                adapter_name,
                f"contract.capabilities.adapters.{raw_name}.adapter",
                issues,
                required=False,
            )
            normalized_status = _normalize_token(status) if status else "unknown"
            if normalized_status not in CAPABILITY_STATUSES:
                _issue(issues, "invalid_value", f"capability adapter status {status!r} is not recognized")
            adapter_records[token] = {"status": normalized_status, "adapter": adapter}
    else:
        for index, raw_item in enumerate(adapters[:MAX_CONTRACT_ITEMS]):
            item_map = _mapping(raw_item, f"contract.capabilities.adapters[{index}]", issues)
            if item_map is None:
                continue
            name = _text(item_map.get("capability"), f"contract.capabilities.adapters[{index}].capability", issues)
            status = _text(item_map.get("status"), f"contract.capabilities.adapters[{index}].status", issues)
            adapter = _text(
                item_map.get("adapter", item_map.get("name")),
                f"contract.capabilities.adapters[{index}].adapter",
                issues,
                required=False,
            )
            if name is not None:
                token = _normalize_token(name)
                if token in adapter_records:
                    _issue(issues, "duplicate_id", f"duplicate capability adapter {name!r}")
                normalized_status = _normalize_token(status) if status else "unknown"
                if normalized_status not in CAPABILITY_STATUSES:
                    _issue(issues, "invalid_value", f"capability adapter status {status!r} is not recognized")
                adapter_records[token] = {"status": normalized_status, "adapter": adapter}

    for capability in required_tokens:
        record = adapter_records.get(capability, {"status": "unreported", "adapter": None})
        status = record["status"]
        report["adapters"].append(
            {"capability": capability, "status": status, "adapter": record["adapter"]}
        )
        if status in {"available", "adapted"}:
            report["satisfied"].append(capability)
        else:
            report["unmet"].append(capability)
            _issue(issues, "capability_unmet", f"required capability {capability!r} is {status}")
    report["required"] = required_tokens


def _validate_descriptors(
    contract: dict[str, Any], issues: list[Issue], warnings: list[Issue], report: dict[str, Any]
) -> None:
    descriptor_data = contract.get("descriptors")
    if descriptor_data is None:
        return
    descriptor_map = _mapping(descriptor_data, "contract.descriptors", issues)
    if descriptor_map is None:
        return
    requested = _canonical_descriptor_map(
        descriptor_map.get("requested", {}), "contract.descriptors.requested", issues
    )
    delivered = _canonical_descriptor_map(
        descriptor_map.get("delivered", {}), "contract.descriptors.delivered", issues
    )
    if requested is None or delivered is None:
        return
    hard_keys = _canonical_key_list(descriptor_map.get("hard_keys", []), "contract.descriptors.hard_keys", issues)
    soft_keys = _canonical_key_list(descriptor_map.get("soft_keys", []), "contract.descriptors.soft_keys", issues)
    if hard_keys & soft_keys:
        _issue(issues, "invalid_value", "contract.descriptors.hard_keys and soft_keys must not overlap")
    unknown_classifications = (hard_keys | soft_keys) - set(requested)
    if unknown_classifications:
        _issue(issues, "invalid_value", f"descriptor classification has unknown keys: {sorted(unknown_classifications)}")

    report["requested"] = {key: requested[key] for key in sorted(requested)}
    report["delivered"] = {key: delivered[key] for key in sorted(delivered)}
    for key in sorted(requested):
        hardness = "soft" if key in soft_keys else "hard"
        preserved = key in delivered and delivered[key] == requested[key]
        entry = {
            "key": key,
            "hardness": hardness,
            "status": "preserved" if preserved else "unmet",
            "requested": requested[key],
            "delivered": delivered.get(key),
        }
        if preserved:
            continue
        report["drift"].append(entry)
        if hardness == "hard":
            _issue(issues, "descriptor_drift", f"hard descriptor {key!r} was not preserved")
        else:
            _warning(warnings, "descriptor_drift", f"soft descriptor {key!r} was not preserved")
    report["added"] = sorted(set(delivered) - set(requested))

    baseline = descriptor_map.get("baseline")
    if baseline is not None:
        baseline_map = _canonical_descriptor_map(
            baseline, "contract.descriptors.baseline", issues
        )
        if baseline_map is not None:
            for key in sorted(set(requested) & set(baseline_map)):
                if requested[key] == baseline_map[key] and delivered.get(key) != baseline_map[key]:
                    hardness = "soft" if key in soft_keys else "hard"
                    entry = {
                        "key": key,
                        "hardness": hardness,
                        "baseline": baseline_map[key],
                        "delivered": delivered.get(key),
                    }
                    report["regressions"].append(entry)
                    if hardness == "hard":
                        _issue(issues, "descriptor_regression", f"descriptor {key!r} regressed from the approved baseline")
                    else:
                        _warning(warnings, "descriptor_regression", f"soft descriptor {key!r} regressed from the approved baseline")


def _validate_contract(
    case: dict[str, Any], issues: list[Issue], warnings: list[Issue], *, required: bool
) -> dict[str, Any]:
    contract_value = case.get("contract")
    if contract_value is None:
        if required:
            _issue(issues, "missing_value", "contract must be provided for schema 1.1 cases")
        return _empty_contract_report()
    contract = _mapping(contract_value, "contract", issues)
    if contract is None:
        return _empty_contract_report(present=True)
    report = _empty_contract_report(present=True)
    constraints = _list(contract.get("constraints", []), "contract.constraints", issues)
    if constraints is not None:
        if len(constraints) > MAX_CONTRACT_ITEMS:
            _issue(issues, "too_many_items", f"contract.constraints must contain at most {MAX_CONTRACT_ITEMS} items")
        seen_ids: set[str] = set()
        for index, item in enumerate(constraints[:MAX_CONTRACT_ITEMS]):
            item_map = _mapping(item, f"contract.constraints[{index}]", issues)
            if item_map is None:
                continue
            item_id = _text(item_map.get("id"), f"contract.constraints[{index}].id", issues)
            hardness = _text(item_map.get("hardness"), f"contract.constraints[{index}].hardness", issues)
            comparison = _text(
                item_map.get("comparison", "exact"),
                f"contract.constraints[{index}].comparison",
                issues,
            )
            normalized_hardness = _normalize_token(hardness) if hardness else None
            normalized_comparison = _normalize_token(comparison) if comparison else None
            if normalized_hardness not in CONTRACT_HARDNESS:
                _issue(issues, "invalid_value", f"contract.constraints[{index}].hardness must be hard or soft")
            if normalized_comparison not in CONTRACT_COMPARISONS:
                _issue(issues, "invalid_value", f"contract.constraints[{index}].comparison is not recognized")
            if item_id is not None:
                normalized_id = _normalize_token(item_id)
                if normalized_id in seen_ids:
                    _issue(issues, "duplicate_id", f"duplicate contract constraint id {item_id!r}")
                seen_ids.add(normalized_id)
            requested_present = "requested" in item_map
            delivered_present = "delivered" in item_map
            outcome = "unknown"
            if not requested_present:
                _issue(issues, "missing_value", f"contract.constraints[{index}].requested must be provided")
            elif normalized_comparison in CONTRACT_COMPARISONS and delivered_present:
                comparison_result = _compare_contract_values(
                    item_map["requested"], item_map["delivered"], normalized_comparison
                )
                if comparison_result is None:
                    _issue(issues, "invalid_value", f"contract.constraints[{index}] has incompatible comparison values")
                else:
                    outcome = "preserved" if comparison_result else "unmet"
            elif requested_present:
                outcome = "unmet"
            if outcome == "preserved":
                report["preserved"] += 1
            elif outcome == "unmet":
                report["unmet"] += 1
                if normalized_hardness == "hard":
                    _issue(issues, "hard_constraint_unmet", f"hard constraint {item_id!r} was not preserved")
                elif normalized_hardness == "soft":
                    _warning(warnings, "soft_constraint_unmet", f"soft constraint {item_id!r} was not preserved")
            else:
                report["unknown"] += 1
            entry = {
                "id": item_id,
                "hardness": normalized_hardness,
                "comparison": normalized_comparison,
                "status": outcome,
            }
            if requested_present:
                entry["requested"] = item_map["requested"]
            if delivered_present:
                entry["delivered"] = item_map["delivered"]
            report["constraints"].append(entry)

    _validate_status_items(contract, "ambiguities", issues, report["ambiguities"])
    _validate_status_items(contract, "conflicts", issues, report["conflicts"])
    _validate_capabilities(contract, issues, report["capabilities"])
    _validate_descriptors(contract, issues, warnings, report["descriptors"])
    return report


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
            "warnings": [],
            "contract": _empty_contract_report(),
            "criteria_basis": None,
        }

    warnings: list[Issue] = []
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
    contract_report = _validate_contract(case, issues, warnings, required=False)

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
        "warnings": [warning.as_dict() for warning in warnings],
        "contract": contract_report,
        "criteria_basis": criteria_basis,
    }


def validate_manifest(data: Any) -> dict[str, Any]:
    """Return a deterministic pass/hold report for untrusted decoded JSON."""
    report: dict[str, Any] = {
        "status": "hold",
        "manifest_id": None,
        "schema_version": None,
        "case_count": 0,
        "passed": 0,
        "held": 0,
        "reasons": [],
        "cases": [],
        "contract_summary": {
            "cases_with_contract": 0,
            "constraints": {"preserved": 0, "unmet": 0, "unknown": 0},
            "capabilities": {"required": 0, "satisfied": 0, "unmet": 0},
            "descriptor_drift": 0,
            "descriptor_regressions": 0,
        },
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
    report["schema_version"] = schema_version
    if schema_version not in {"1.0", "1.1"}:
        _issue(manifest_issues, "unsupported_schema", "schema_version must be '1.0' or '1.1'")

    cases = _list(data.get("cases"), "cases", manifest_issues)
    if cases is not None:
        if not cases:
            _issue(manifest_issues, "missing_value", "cases must contain at least one case")
        if len(cases) > MAX_CASES:
            _issue(manifest_issues, "too_many_cases", f"cases must contain at most {MAX_CASES} cases")
        seen_ids: set[str] = set()
        for index, case in enumerate(cases[:MAX_CASES]):
            result = _validate_case(case, index)
            if schema_version == "1.1" and isinstance(case, dict):
                if "contract" not in case or case.get("contract") is None:
                    result["reasons"].append(
                        {"code": "missing_value", "message": "contract must be provided for schema 1.1 cases"}
                    )
                    result["status"] = "hold"
            if result["id"] in seen_ids:
                result["reasons"].append({"code": "duplicate_id", "message": f"duplicate case id {result['id']!r}"})
                result["status"] = "hold"
            seen_ids.add(result["id"])
            report["cases"].append(result)

            contract = result["contract"]
            if contract["present"]:
                report["contract_summary"]["cases_with_contract"] += 1
            for count_name in ("preserved", "unmet", "unknown"):
                report["contract_summary"]["constraints"][count_name] += contract[count_name]
            report["contract_summary"]["capabilities"]["required"] += len(contract["capabilities"]["required"])
            report["contract_summary"]["capabilities"]["satisfied"] += len(contract["capabilities"]["satisfied"])
            report["contract_summary"]["capabilities"]["unmet"] += len(contract["capabilities"]["unmet"])
            report["contract_summary"]["descriptor_drift"] += len(contract["descriptors"]["drift"])
            report["contract_summary"]["descriptor_regressions"] += len(contract["descriptors"]["regressions"])

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
        for warning in case.get("warnings", []):
            lines.append(f"  - warning [{warning['code']}] {warning['message']}")
        contract = case.get("contract", {})
        if contract.get("present"):
            lines.append(
                "  - contract: "
                f"preserved={contract.get('preserved', 0)}, "
                f"unmet={contract.get('unmet', 0)}, "
                f"unknown={contract.get('unknown', 0)}"
            )
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
