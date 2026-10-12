"""Tests for ComfyUI Wan 2.1 / 2.2 video generation client, CLI, and MCP server.

tags: [test, comfyui, wan22, video, harness, mcp]
routing_hints: [test, video, comfy]
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
for _p in (str(_SCRIPTS_DIR / "_lib"), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.test_comfy_video import ComfyVideoClient, DEFAULT_PROMPT
from tools.comfy_video_mcp_server import TOOLS_REGISTRY, dispatch_tool
from cli.harness import build_parser, main


class TestComfyVideoIntegration(unittest.TestCase):
    def test_build_wan22_prompt_structure(self) -> None:
        """Verify that build_wan22_prompt constructs a fully valid 16-node graph."""
        client = ComfyVideoClient(server="127.0.0.1:8188")
        prompt_graph = client.build_wan22_prompt(
            prompt="A robotic astronaut floating in zero gravity",
            length=17,
            width=640,
            height=640,
            steps=4,
            fps=16.0,
            seed=42,
        )

        # Core node IDs
        expected_nodes = {"71", "73", "75", "76", "83", "85", "82", "86", "74", "89", "72", "81", "78", "87", "114", "115"}
        self.assertEqual(set(prompt_graph.keys()), expected_nodes)

        # Check positive text prompt
        self.assertEqual(prompt_graph["89"]["class_type"], "CLIPTextEncode")
        self.assertEqual(prompt_graph["89"]["inputs"]["text"], "A robotic astronaut floating in zero gravity")
        self.assertEqual(prompt_graph["89"]["inputs"]["clip"], ["71", 0])

        # Check dimensions and frames
        self.assertEqual(prompt_graph["74"]["class_type"], "EmptyHunyuanLatentVideo")
        self.assertEqual(prompt_graph["74"]["inputs"]["length"], 17)
        self.assertEqual(prompt_graph["74"]["inputs"]["width"], 640)
        self.assertEqual(prompt_graph["74"]["inputs"]["height"], 640)

        # Check dual-UNet LoRA loaders
        self.assertEqual(prompt_graph["83"]["class_type"], "LoraLoaderModelOnly")
        self.assertIn("high_noise", prompt_graph["83"]["inputs"]["lora_name"])
        self.assertEqual(prompt_graph["85"]["class_type"], "LoraLoaderModelOnly")
        self.assertIn("low_noise", prompt_graph["85"]["inputs"]["lora_name"])

        # Check output video node
        self.assertEqual(prompt_graph["115"]["class_type"], "SaveVideo")
        self.assertEqual(prompt_graph["115"]["inputs"]["video"], ["114", 0])

    def test_mcp_tools_registry(self) -> None:
        """Verify MCP tools definition has the required 3 tools with valid schemas."""
        tool_names = [t["name"] for t in TOOLS_REGISTRY]
        self.assertIn("video_generate", tool_names)
        self.assertIn("video_status", tool_names)
        self.assertIn("video_list_models", tool_names)

        gen_tool = next(t for t in TOOLS_REGISTRY if t["name"] == "video_generate")
        self.assertIn("prompt", gen_tool["inputSchema"]["properties"])
        self.assertIn("length", gen_tool["inputSchema"]["properties"])
        self.assertIn("wait", gen_tool["inputSchema"]["properties"])

    def test_mcp_dispatch_unknown(self) -> None:
        """Verify dispatch_tool returns error on unknown tool."""
        res = dispatch_tool("non_existent_tool", {})
        self.assertFalse(res["ok"])
        self.assertIn("Unknown tool name", res["error"])

    def test_harness_cli_video_parser(self) -> None:
        """Test harness CLI parser handles video subcommands."""
        parser = build_parser()

        # Test status args
        args_status = parser.parse_args(["video", "status"])
        self.assertEqual(args_status.cmd, "video")
        self.assertEqual(args_status.video_cmd, "status")

        # Test models args
        args_models = parser.parse_args(["video", "models"])
        self.assertEqual(args_models.cmd, "video")
        self.assertEqual(args_models.video_cmd, "models")

        # Test generate args
        args_gen = parser.parse_args(["video", "generate", "--prompt", "cyberpunk car", "--length", "33", "--no-wait"])
        self.assertEqual(args_gen.cmd, "video")
        self.assertEqual(args_gen.video_cmd, "generate")
        self.assertEqual(args_gen.prompt, "cyberpunk car")
        self.assertEqual(args_gen.length, 33)
        self.assertTrue(args_gen.no_wait)

    def test_harness_cli_video_models_execution(self) -> None:
        """Test harness video models prints installed Wan models."""
        with tempfile.TemporaryDirectory() as td:
            models_dir = Path(td)
            diff_dir = models_dir / "diffusion_models"
            diff_dir.mkdir(parents=True, exist_ok=True)
            mock_model = diff_dir / "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
            mock_model.write_text("model", encoding="utf-8")

            loras_dir = models_dir / "loras"
            loras_dir.mkdir(parents=True, exist_ok=True)
            mock_lora = loras_dir / "wan2.2_lightx2v_4step_lora.safetensors"
            mock_lora.write_text("lora", encoding="utf-8")

            stdout_buf = io.StringIO()
            with patch("sys.stdout", stdout_buf):
                ret = main(["video", "models", "--models-dir", str(models_dir)])

            self.assertEqual(ret, 0)
            output = stdout_buf.getvalue()
            self.assertIn("DIFFUSION_MODELS", output)
            self.assertIn("wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors", output)
            self.assertIn("LORAS", output)


if __name__ == "__main__":
    unittest.main()
