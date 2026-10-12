"""Model Context Protocol (MCP) Stdio Server for ComfyUI Wan 2.1 / 2.2 Video Generation.

Exposes native tools for LLM and coding agents (Bionic, Antigravity, Cursor) to:
- Generate text-to-video using local Wan 2.2 models
- Query execution queue and active generation progress
- List installed Wan models, LoRAs, and VAEs

tags: [mcp, server, comfyui, wan22, video, tools, jsonrpc, stdio]
routing_hints: [comfy-video-mcp, video-mcp, video-tools]
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any

# Ensure scripts and _lib are in sys.path
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_LIB_DIR = _SCRIPTS_DIR / "_lib"
for _p in (str(_LIB_DIR), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.test_comfy_video import (
    ComfyVideoClient,
    DEFAULT_NEGATIVE_PROMPT,
    DEFAULT_PROMPT,
    DEFAULT_SERVER,
)

SERVER_NAME = "comfy-video-mcp-server"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("comfy_video_mcp")

TOOLS_REGISTRY = [
    {
        "name": "video_generate",
        "description": (
            "Generate a video from a text prompt using the local ComfyUI Wan 2.1 / 2.2 model. "
            "Supports customizable dimensions, frame count, sampling steps, and synchronous "
            "or non-blocking async execution."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Positive text description of the desired video scene.",
                    "default": DEFAULT_PROMPT,
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Negative text prompt describing elements to avoid.",
                    "default": DEFAULT_NEGATIVE_PROMPT,
                },
                "length": {
                    "type": "integer",
                    "description": "Number of frames to generate (e.g. 17 frames = ~1 sec, 81 frames = ~5 sec at 16 fps).",
                    "default": 17,
                },
                "width": {
                    "type": "integer",
                    "description": "Video frame width in pixels (e.g. 640 or 480).",
                    "default": 640,
                },
                "height": {
                    "type": "integer",
                    "description": "Video frame height in pixels (e.g. 640 or 480).",
                    "default": 640,
                },
                "steps": {
                    "type": "integer",
                    "description": "Number of sampling steps (default 4 for Wan 2.2 Lightx2v LoRA).",
                    "default": 4,
                },
                "fps": {
                    "type": "number",
                    "description": "Frames per second for output video playback.",
                    "default": 16.0,
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for generation reproducibility.",
                },
                "wait": {
                    "type": "boolean",
                    "description": "If true, blocks until generation completes and downloads the MP4 file. If false, returns immediately with prompt_id.",
                    "default": True,
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory where downloaded video files will be stored.",
                    "default": "results/video",
                },
                "server": {
                    "type": "string",
                    "description": "ComfyUI host and port.",
                    "default": DEFAULT_SERVER,
                },
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "video_status",
        "description": "Check the status of the local ComfyUI generation queue or query a specific prompt execution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt_id": {
                    "type": "string",
                    "description": "Optional prompt ID to check in execution history.",
                },
                "server": {
                    "type": "string",
                    "description": "ComfyUI host and port.",
                    "default": DEFAULT_SERVER,
                },
            },
        },
    },
    {
        "name": "video_list_models",
        "description": "List available Wan 2.1 / 2.2 diffusion models, LoRAs, VAEs, and text encoders installed in ComfyUI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "models_dir": {
                    "type": "string",
                    "description": "Path to ComfyUI models directory.",
                    "default": r"D:\Code\wan22\ComfyUI_windows_portable\ComfyUI\models",
                },
            },
        },
    },
]


def handle_video_generate(arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute or queue video generation."""
    server = arguments.get("server", DEFAULT_SERVER)
    client = ComfyVideoClient(server=server)

    prompt = arguments.get("prompt", DEFAULT_PROMPT)
    negative_prompt = arguments.get("negative_prompt", DEFAULT_NEGATIVE_PROMPT)
    length = arguments.get("length", 17)
    width = arguments.get("width", 640)
    height = arguments.get("height", 640)
    steps = arguments.get("steps", 4)
    fps = arguments.get("fps", 16.0)
    seed = arguments.get("seed")
    wait = arguments.get("wait", True)
    output_dir = arguments.get("output_dir", "results/video")

    client_id = f"mcp_{os.getpid()}"
    prompt_graph = client.build_wan22_prompt(
        prompt=prompt,
        negative_prompt=negative_prompt,
        length=length,
        width=width,
        height=height,
        steps=steps,
        fps=fps,
        seed=seed,
    )

    submit_res = client.submit_prompt(prompt_graph, client_id=client_id)
    prompt_id = submit_res.get("prompt_id")

    if not wait:
        return {
            "ok": True,
            "status": "queued",
            "prompt_id": prompt_id,
            "server": client.base_url,
            "message": f"Video generation queued as prompt_id '{prompt_id}'. Check status using video_status.",
        }

    history = asyncio.run(client.stream_progress_and_wait(prompt_id, client_id=client_id))
    downloaded = client.download_output_video(history, prompt_id, output_dir=output_dir)

    return {
        "ok": True,
        "status": "completed",
        "prompt_id": prompt_id,
        "files": [str(p) for p in downloaded],
        "output_dir": output_dir,
    }


def handle_video_status(arguments: dict[str, Any]) -> dict[str, Any]:
    """Fetch queue and history status."""
    server = arguments.get("server", DEFAULT_SERVER)
    client = ComfyVideoClient(server=server)

    q = client.get_queue()
    prompt_id = arguments.get("prompt_id")
    history_entry = None
    if prompt_id:
        h = client.get_history(prompt_id)
        history_entry = h.get(prompt_id)

    return {
        "ok": True,
        "queue_running": [item[1] for item in q.get("queue_running", [])],
        "queue_pending": [item[1] for item in q.get("queue_pending", [])],
        "history": history_entry,
    }


def handle_video_list_models(arguments: dict[str, Any]) -> dict[str, Any]:
    """Inspect local models directory for Wan components."""
    models_dir = Path(arguments.get("models_dir", r"D:\Code\wan22\ComfyUI_windows_portable\ComfyUI\models"))
    if not models_dir.exists():
        return {"ok": False, "error": f"Models directory not found: {models_dir}"}

    categorized: dict[str, list[dict[str, Any]]] = {
        "diffusion_models": [],
        "loras": [],
        "text_encoders": [],
        "vae": [],
    }

    for cat in categorized:
        p = models_dir / cat
        if p.exists():
            for root, _, files in os.walk(p):
                for f in files:
                    if f.endswith((".safetensors", ".ckpt", ".pt", ".bin")):
                        full_p = Path(root) / f
                        rel_p = full_p.relative_to(p)
                        size_gb = round(full_p.stat().st_size / (1024**3), 2)
                        categorized[cat].append({
                            "name": str(rel_p).replace("\\", "/"),
                            "size_gb": size_gb,
                        })

    return {
        "ok": True,
        "models_dir": str(models_dir),
        "models": categorized,
    }


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool call to appropriate handler."""
    if name == "video_generate":
        return handle_video_generate(arguments)
    elif name == "video_status":
        return handle_video_status(arguments)
    elif name == "video_list_models":
        return handle_video_list_models(arguments)
    else:
        return {"ok": False, "error": f"Unknown tool name '{name}'"}


def main() -> None:
    """Run JSON-RPC 2.0 MCP server loop reading from stdin and writing to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception:
            continue

        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            continue

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS_REGISTRY,
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                outcome = dispatch_tool(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(outcome, indent=2),
                            }
                        ],
                        "isError": not outcome.get("ok", True),
                    },
                }
            except Exception as e:
                logger.exception("Error executing tool %s: %s", tool_name, e)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"ok": False, "error": str(e)}, indent=2),
                            }
                        ],
                        "isError": True,
                    },
                }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
