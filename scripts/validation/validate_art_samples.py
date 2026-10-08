"""Validate the declared sample gallery's routes and local package paths.

tags: [validation, art-router, samples]
routing_hints: [sample-gallery, package-paths, representation-registry]

This check proves only that declared files exist inside the repository package
and that their route/type metadata is registered. It does not inspect artwork.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GALLERY = REPOSITORY_ROOT / "ai-tooling" / "skills" / "artistic" / "representation-routing" / "sample-gallery.json"
MAX_GALLERY_BYTES = 256 * 1024
EXPECTED_PATHS = {
    "ai-tooling/skills/artistic/representation-routing/sample-collage.png",
    "ai-tooling/skills/artistic/representation-routing/sample-comic-strip.png",
    "ai-tooling/skills/artistic/representation-routing/sample-pixel-sprite-sheet.png",
    "ai-tooling/skills/artistic/representation-routing/sample-editorial-photo.png",
    "ai-tooling/skills/artistic/representation-routing/sample-3d-concept-render.png",
    "ai-tooling/skills/artistic/representation-routing/sample-vector-poster.svg",
}
FORMAT_SUFFIXES = {"image/png": ".png", "image/svg+xml": ".svg"}

sys.path.insert(0, str(REPOSITORY_ROOT / "scripts" / "validation"))
from validate_art_router import REPRESENTATIONS_BY_ID, _canonical_asset_type, _resolve_medium  # noqa: E402


def _issue(issues: list[str], message: str) -> None:
    issues.append(message)


def validate_sample_gallery(
    root: Path = REPOSITORY_ROOT,
    gallery_path: Path = DEFAULT_GALLERY,
) -> dict[str, Any]:
    issues: list[str] = []
    root = root.resolve()
    try:
        gallery_path = gallery_path.resolve(strict=True)
        gallery_path.relative_to(root)
        raw = gallery_path.read_bytes()
    except (OSError, ValueError):
        return {
            "status": "hold",
            "sample_count": 0,
            "checked_paths": [],
            "reasons": ["sample gallery must be a readable file inside the repository root"],
        }
    if len(raw) > MAX_GALLERY_BYTES:
        return {
            "status": "hold",
            "sample_count": 0,
            "checked_paths": [],
            "reasons": [f"sample gallery exceeds {MAX_GALLERY_BYTES} bytes"],
        }
    try:
        gallery = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "status": "hold",
            "sample_count": 0,
            "checked_paths": [],
            "reasons": ["sample gallery must be UTF-8 JSON"],
        }
    if not isinstance(gallery, dict):
        return {
            "status": "hold",
            "sample_count": 0,
            "checked_paths": [],
            "reasons": ["sample gallery must be a JSON object"],
        }
    if gallery.get("schema_version") != "1.0":
        _issue(issues, "schema_version must be '1.0'")
    if gallery.get("registry") != "docs/standards/artistic-representation-registry.json":
        _issue(issues, "registry must point to the canonical representation registry")
    if gallery.get("package_root") != "ai-tooling/skills/artistic/representation-routing":
        _issue(issues, "package_root must be the representation-routing skill folder")
    samples = gallery.get("samples")
    if not isinstance(samples, list):
        samples = []
        _issue(issues, "samples must be an array")
    if len(samples) != len(EXPECTED_PATHS):
        _issue(issues, f"samples must declare exactly {len(EXPECTED_PATHS)} reserved artwork files")

    checked_paths: list[str] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, sample in enumerate(samples):
        field = f"samples[{index}]"
        if not isinstance(sample, dict):
            _issue(issues, f"{field} must be an object")
            continue
        sample_id = sample.get("id")
        route_name = sample.get("representation")
        asset_type = sample.get("asset_type")
        format_name = sample.get("format")
        path_value = sample.get("path")
        if not isinstance(sample_id, str) or not sample_id.strip():
            _issue(issues, f"{field}.id must be a non-empty string")
        elif sample_id in seen_ids:
            _issue(issues, f"duplicate sample id {sample_id!r}")
        else:
            seen_ids.add(sample_id)

        route_id = _resolve_medium(route_name) if isinstance(route_name, str) else None
        route = REPRESENTATIONS_BY_ID.get(route_id) if route_id else None
        if route is None:
            _issue(issues, f"{field}.representation must resolve to a registered route")
        if not isinstance(asset_type, str) or not asset_type.strip():
            _issue(issues, f"{field}.asset_type must be a non-empty string")
        elif route is not None and _canonical_asset_type(route, asset_type) is None:
            _issue(issues, f"{field}.asset_type is not registered for representation {route_id!r}")

        if not isinstance(format_name, str) or format_name not in FORMAT_SUFFIXES:
            _issue(issues, f"{field}.format must be image/png or image/svg+xml")
        if not isinstance(path_value, str) or not path_value:
            _issue(issues, f"{field}.path must be a non-empty repository-relative path")
            continue
        posix_path = PurePosixPath(path_value)
        windows_path = PureWindowsPath(path_value)
        if (
            posix_path.is_absolute()
            or windows_path.is_absolute()
            or windows_path.drive
            or "\\" in path_value
            or any(part in {"", ".", ".."} for part in posix_path.parts)
        ):
            _issue(issues, f"{field}.path must be a normalized repository-relative POSIX path")
            continue
        if path_value in seen_paths:
            _issue(issues, f"duplicate sample path {path_value!r}")
        seen_paths.add(path_value)
        if path_value not in EXPECTED_PATHS:
            _issue(issues, f"{field}.path is not one of the six reserved artwork files")
        if isinstance(format_name, str) and format_name in FORMAT_SUFFIXES:
            if posix_path.suffix.lower() != FORMAT_SUFFIXES[format_name]:
                _issue(issues, f"{field}.format does not match the file extension")
        try:
            resolved_path = root.joinpath(*posix_path.parts).resolve(strict=True)
            resolved_path.relative_to(root)
            if not resolved_path.is_file():
                _issue(issues, f"{field}.path is not a file")
            else:
                checked_paths.append(path_value)
        except (OSError, ValueError):
            _issue(issues, f"{field}.path does not resolve to a file inside the repository")

    if seen_paths != EXPECTED_PATHS:
        missing = sorted(EXPECTED_PATHS - seen_paths)
        extra = sorted(seen_paths - EXPECTED_PATHS)
        if missing:
            _issue(issues, f"reserved sample paths missing from gallery: {missing}")
        if extra:
            _issue(issues, f"unreserved sample paths found in gallery: {extra}")

    return {
        "status": "pass" if not issues else "hold",
        "sample_count": len(samples),
        "checked_paths": sorted(checked_paths),
        "reasons": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check art sample route metadata and local package paths.")
    parser.add_argument("--gallery", type=Path, default=DEFAULT_GALLERY, help="sample gallery JSON")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a JSON report")
    args = parser.parse_args(argv)
    report = validate_sample_gallery(REPOSITORY_ROOT, args.gallery)
    if args.as_json:
        print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
    else:
        print(f"status: {report['status']}")
        print(f"samples: {report['sample_count']}")
        for path in report["checked_paths"]:
            print(f"checked: {path}")
        for reason in report["reasons"]:
            print(f"issue: {reason}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
