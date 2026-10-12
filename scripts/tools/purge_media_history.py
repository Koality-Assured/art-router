"""Media History and Prompt Purge Utility for Local ComfyUI Workflows.

Purges in-memory execution queues, strips prompt metadata from generated MP4s,
deletes temporary video artifacts, and cleans PowerShell history traces.

tags: [artistic, privacy, cleanup, comfyui, video]
routing_hints: [purge, cleanup, privacy, comfyui, history, metadata, sanitize]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("media_purge")

DEFAULT_SERVER = "127.0.0.1:8188"
DEFAULT_OUTPUT_DIRS = [
    Path.home() / "Videos" / "Generated",
    Path(r"D:\Code\wan22\ComfyUI_windows_portable\ComfyUI\output"),
]
PS_HISTORY_PATH = (
    Path(os.environ.get("APPDATA", ""))
    / "Microsoft"
    / "Windows"
    / "PowerShell"
    / "PSReadLine"
    / "ConsoleHost_history.txt"
)
DEFAULT_FILTER_PATTERNS = [
    r"\bcomfy-video\b",
    r"\bharness\s+video\b",
    r"\bwan22\b",
    r"\bwan\s*2\.[12]\b",
    r"\b--prompt\b",
]


def clear_comfy_history(server: str = DEFAULT_SERVER, dry_run: bool = False) -> dict[str, Any]:
    """Clear ComfyUI in-memory execution history via POST /history {"clear": true}."""
    base_url = f"http://{server}" if not server.startswith("http") else server
    url = f"{base_url.rstrip('/')}/history"

    if dry_run:
        logger.info("[DRY-RUN] Would send POST %s with {'clear': True}", url)
        return {"status": "dry_run", "target": url}

    payload = json.dumps({"clear": True}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
        logger.info("ComfyUI in-memory execution history cleared successfully.")
        return {"status": "cleared", "server": base_url}
    except urllib.error.URLError as e:
        logger.info("ComfyUI server at %s is offline (%s); in-memory history is already clean.", base_url, e)
        return {"status": "offline", "server": base_url, "note": "Server offline; RAM history already clean"}


def strip_video_metadata(
    directories: list[Path] | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Strip embedded prompt and workflow metadata from MP4/video files using ffmpeg."""
    target_dirs = directories or DEFAULT_OUTPUT_DIRS
    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe and not dry_run:
        logger.warning("ffmpeg executable not found in PATH; cannot strip metadata.")
        return []

    results: list[dict[str, Any]] = []
    for d in target_dirs:
        if not d.exists():
            continue
        for ext in ("*.mp4", "*.webm", "*.mkv"):
            for file_path in d.glob(ext):
                if file_path.name.endswith(".clean.mp4") or file_path.name.startswith("temp_"):
                    continue
                temp_path = file_path.with_name(f"temp_strip_{file_path.name}")
                if dry_run:
                    logger.info("[DRY-RUN] Would strip metadata from: %s", file_path)
                    results.append({"file": str(file_path), "action": "dry_run_strip"})
                    continue

                try:
                    cmd = [
                        ffmpeg_exe,
                        "-y",
                        "-i",
                        str(file_path),
                        "-map_metadata",
                        "-1",
                        "-c",
                        "copy",
                        str(temp_path),
                    ]
                    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                    if proc.returncode == 0 and temp_path.exists() and temp_path.stat().st_size > 0:
                        file_path.unlink()
                        temp_path.rename(file_path)
                        logger.info("Stripped metadata: %s", file_path.name)
                        results.append({"file": str(file_path), "action": "stripped", "status": "ok"})
                    else:
                        if temp_path.exists():
                            temp_path.unlink()
                        logger.error("Failed to strip metadata from %s: %s", file_path.name, proc.stderr)
                        results.append({"file": str(file_path), "action": "strip_failed", "error": proc.stderr})
                except Exception as exc:
                    if temp_path.exists():
                        temp_path.unlink()
                    logger.error("Exception stripping metadata from %s: %s", file_path, exc)
                    results.append({"file": str(file_path), "action": "error", "error": str(exc)})
    return results


def delete_generated_videos(
    directories: list[Path] | None = None,
    dry_run: bool = False,
) -> list[str]:
    """Delete generated video artifacts from output directories."""
    target_dirs = directories or DEFAULT_OUTPUT_DIRS
    deleted: list[str] = []
    for d in target_dirs:
        if not d.exists():
            continue
        for ext in ("*.mp4", "*.webm", "*.mkv"):
            for file_path in d.glob(ext):
                if dry_run:
                    logger.info("[DRY-RUN] Would delete video file: %s", file_path)
                    deleted.append(str(file_path))
                    continue
                try:
                    file_path.unlink()
                    logger.info("Deleted video artifact: %s", file_path.name)
                    deleted.append(str(file_path))
                except Exception as exc:
                    logger.error("Failed to delete %s: %s", file_path, exc)
    return deleted


def clean_powershell_history(
    history_file: Path | None = None,
    patterns: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Remove command history lines containing local video prompts or execution flags."""
    target_file = history_file or PS_HISTORY_PATH
    if not target_file.exists():
        logger.info("PowerShell history file does not exist at %s.", target_file)
        return {"status": "not_found", "file": str(target_file)}

    regexes = [re.compile(p, re.IGNORECASE) for p in (patterns or DEFAULT_FILTER_PATTERNS)]
    try:
        lines = target_file.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        logger.error("Failed to read history file %s: %s", target_file, exc)
        return {"status": "read_error", "error": str(exc)}

    kept_lines: list[str] = []
    removed_count = 0
    removed_samples: list[str] = []

    for line in lines:
        if any(r.search(line) for r in regexes):
            removed_count += 1
            if len(removed_samples) < 5:
                removed_samples.append(line)
        else:
            kept_lines.append(line)

    if dry_run:
        logger.info(
            "[DRY-RUN] Would remove %d matching lines from %s (keeping %d lines).",
            removed_count,
            target_file,
            len(kept_lines),
        )
        return {
            "status": "dry_run",
            "file": str(target_file),
            "total_lines": len(lines),
            "removed_lines": removed_count,
            "kept_lines": len(kept_lines),
            "samples": removed_samples,
        }

    if removed_count > 0:
        try:
            target_file.write_text("\n".join(kept_lines) + ("\n" if kept_lines else ""), encoding="utf-8")
            logger.info("Purged %d history entries from %s.", removed_count, target_file)
        except Exception as exc:
            logger.error("Failed to write sanitized history file: %s", exc)
            return {"status": "write_error", "error": str(exc)}

    return {
        "status": "purged",
        "file": str(target_file),
        "total_lines": len(lines),
        "removed_lines": removed_count,
        "kept_lines": len(kept_lines),
    }


def purge_all(
    server: str = DEFAULT_SERVER,
    directories: list[Path] | None = None,
    delete_videos: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute complete cleanup: ComfyUI in-memory queue, file metadata/deletion, and PowerShell history."""
    report: dict[str, Any] = {
        "comfy_queue": clear_comfy_history(server=server, dry_run=dry_run),
        "shell_history": clean_powershell_history(dry_run=dry_run),
    }
    if delete_videos:
        report["deleted_videos"] = delete_generated_videos(directories=directories, dry_run=dry_run)
    else:
        report["stripped_metadata"] = strip_video_metadata(directories=directories, dry_run=dry_run)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Purge local ComfyUI execution history, video metadata, and terminal prompt traces."
    )
    parser.add_argument("--all", action="store_true", help="Execute complete cleanup across ComfyUI, files, and shell history")
    parser.add_argument("--comfy-history", action="store_true", help="Clear ComfyUI in-memory execution queue/history")
    parser.add_argument("--strip-metadata", action="store_true", help="Losslessly strip embedded prompt metadata from MP4 files")
    parser.add_argument("--delete-videos", action="store_true", help="Delete generated video files from output folders")
    parser.add_argument("--shell-history", action="store_true", help="Clean video prompt entries from PowerShell history")
    parser.add_argument("--dry-run", action="store_true", help="Simulate cleanup without modifying state or deleting files")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="ComfyUI server address (default: 127.0.0.1:8188)")
    parser.add_argument("--target-dir", action="append", help="Specific directory to purge (can be passed multiple times)")
    parser.add_argument("--json", action="store_true", help="Format output as JSON")

    args = parser.parse_args(argv)

    if not any([args.all, args.comfy_history, args.strip_metadata, args.delete_videos, args.shell_history]):
        # Default to safe preview if no explicit action passed
        args.all = True
        args.dry_run = True
        logger.info("No explicit cleanup flags specified; running in safe --dry-run mode.")

    target_dirs = [Path(p) for p in args.target_dir] if args.target_dir else None
    report: dict[str, Any] = {}

    if args.all:
        report = purge_all(server=args.server, directories=target_dirs, delete_videos=args.delete_videos, dry_run=args.dry_run)
    else:
        if args.comfy_history:
            report["comfy_queue"] = clear_comfy_history(server=args.server, dry_run=args.dry_run)
        if args.delete_videos:
            report["deleted_videos"] = delete_generated_videos(directories=target_dirs, dry_run=args.dry_run)
        elif args.strip_metadata:
            report["stripped_metadata"] = strip_video_metadata(directories=target_dirs, dry_run=args.dry_run)
        if args.shell_history:
            report["shell_history"] = clean_powershell_history(dry_run=args.dry_run)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("\n=== Media Privacy & History Purge Summary ===")
    if "comfy_queue" in report:
        print(f"ComfyUI Queue:     {report['comfy_queue'].get('status')}")
    if "stripped_metadata" in report:
        print(f"Stripped Files:    {len(report['stripped_metadata'])}")
        for f in report["stripped_metadata"]:
            print(f"  - {f.get('file')}: {f.get('action')}")
    if "deleted_videos" in report:
        print(f"Deleted Videos:    {len(report['deleted_videos'])}")
        for f in report["deleted_videos"]:
            print(f"  - {f}")
    if "shell_history" in report:
        sh = report["shell_history"]
        print(f"PowerShell Lines:  Purged {sh.get('removed_lines', 0)} entries (Remaining: {sh.get('kept_lines', 0)})")
    if args.dry_run:
        print("\nNote: Simulated run only (--dry-run). Re-run without --dry-run to apply changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
