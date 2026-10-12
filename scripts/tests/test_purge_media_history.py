"""Unit tests for purge_media_history tool.

tags: [tests, privacy, cleanup, comfyui]
routing_hints: [tests, purge, media-history, cleanup]
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from tools.purge_media_history import (
    clean_powershell_history,
    clear_comfy_history,
    delete_generated_videos,
    strip_video_metadata,
)


class TestPurgeMediaHistory(unittest.TestCase):
    def test_clear_comfy_history_dry_run(self) -> None:
        res = clear_comfy_history(server="127.0.0.1:8188", dry_run=True)
        self.assertEqual(res.get("status"), "dry_run")
        self.assertIn("127.0.0.1:8188/history", res.get("target", ""))

    def test_clean_powershell_history(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            history_file = Path(td) / "ConsoleHost_history.txt"
            initial_content = (
                "git status\n"
                "python scripts/cli/harness.py status\n"
                "comfy-video --prompt \"secret sunset video\" --length 81\n"
                "ls -la\n"
                "harness video generate --prompt \"another private prompt\"\n"
                "pytest\n"
            )
            history_file.write_text(initial_content, encoding="utf-8")

            # Dry run test
            dry_res = clean_powershell_history(history_file=history_file, dry_run=True)
            self.assertEqual(dry_res.get("status"), "dry_run")
            self.assertEqual(dry_res.get("removed_lines"), 2)
            self.assertEqual(dry_res.get("kept_lines"), 4)

            # Mutating run
            run_res = clean_powershell_history(history_file=history_file, dry_run=False)
            self.assertEqual(run_res.get("status"), "purged")
            self.assertEqual(run_res.get("removed_lines"), 2)

            sanitized = history_file.read_text(encoding="utf-8").splitlines()
            self.assertIn("git status", sanitized)
            self.assertIn("ls -la", sanitized)
            self.assertIn("pytest", sanitized)
            self.assertNotIn("comfy-video --prompt \"secret sunset video\" --length 81", sanitized)
            self.assertNotIn("harness video generate --prompt \"another private prompt\"", sanitized)

    def test_delete_generated_videos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_dir = Path(td)
            vid1 = temp_dir / "wan22_test_01.mp4"
            vid2 = temp_dir / "other.webm"
            txt = temp_dir / "notes.txt"
            vid1.write_text("dummy", encoding="utf-8")
            vid2.write_text("dummy", encoding="utf-8")
            txt.write_text("keep me", encoding="utf-8")

            # Dry run
            dry_res = delete_generated_videos(directories=[temp_dir], dry_run=True)
            self.assertEqual(len(dry_res), 2)
            self.assertTrue(vid1.exists())

            # Mutate
            del_res = delete_generated_videos(directories=[temp_dir], dry_run=False)
            self.assertEqual(len(del_res), 2)
            self.assertFalse(vid1.exists())
            self.assertFalse(vid2.exists())
            self.assertTrue(txt.exists())

    def test_strip_video_metadata_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_dir = Path(td)
            vid = temp_dir / "wan22_sample.mp4"
            vid.write_text("dummy", encoding="utf-8")

            res = strip_video_metadata(directories=[temp_dir], dry_run=True)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["action"], "dry_run_strip")


if __name__ == "__main__":
    unittest.main()
