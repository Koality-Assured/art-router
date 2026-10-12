"""End-to-end client and test script for local ComfyUI Wan 2.1 / 2.2 video generation.

Connects to ComfyUI via HTTP REST and WebSocket to:
- Probe queue and object info
- Submit text-to-video prompts using the Wan 2.2 dual-UNet 4-step Lighting LoRA workflow
- Stream live sampling progress (KSampler steps, latents, VAE decoding) over WebSocket
- Capture output video metadata from /history and download the generated MP4 via /view

tags: [comfyui, wan22, video, generation, t2v, tools]
routing_hints: [comfy, video, wan, generation, t2v]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

try:
    import aiohttp
except ImportError:
    aiohttp = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("comfy_video")

DEFAULT_SERVER = "127.0.0.1:8188"
DEFAULT_PROMPT = "A glowing blue futuristic digital cube rotating slowly on a dark reflective surface, 4k, cinematic"
DEFAULT_NEGATIVE_PROMPT = (
    "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，"
    "整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，"
    "画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，"
    "静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走，裸露，NSFW"
)


class ComfyVideoClient:
    """HTTP & WebSocket client for ComfyUI video generation workflows."""

    def __init__(self, server: str = DEFAULT_SERVER) -> None:
        self.server = server.rstrip("/")
        if not self.server.startswith("http://") and not self.server.startswith("https://"):
            self.base_url = f"http://{self.server}"
            self.ws_url = f"ws://{self.server}/ws"
        else:
            self.base_url = self.server
            ws_proto = "wss://" if self.server.startswith("https://") else "ws://"
            host_part = self.server.split("://", 1)[1]
            self.ws_url = f"{ws_proto}{host_part}/ws"

    def get_queue(self) -> dict[str, Any]:
        """Fetch current queue status (running and pending tasks)."""
        url = f"{self.base_url}/queue"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_object_info(self, node_class: str | None = None) -> dict[str, Any]:
        """Query ComfyUI object info for node definitions."""
        url = f"{self.base_url}/object_info"
        if node_class:
            url += f"/{urllib.parse.quote(node_class)}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_history(self, prompt_id: str | None = None) -> dict[str, Any]:
        """Fetch execution history for all or a specific prompt_id."""
        url = f"{self.base_url}/history"
        if prompt_id:
            url += f"/{urllib.parse.quote(prompt_id)}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def build_wan22_prompt(
        self,
        prompt: str = DEFAULT_PROMPT,
        negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
        width: int = 640,
        height: int = 640,
        length: int = 17,
        steps: int = 4,
        shift: float = 5.0,
        fps: float = 16.0,
        seed: int | None = None,
        prefix: str = "wan22_t2v",
    ) -> dict[str, Any]:
        """Construct the prompt dictionary targeting the Wan 2.2 dual-UNet 4-step pipeline."""
        if seed is None:
            seed = random.randint(1, 2**32 - 1)

        # 4-step Lightx2v splits 2 steps high-noise and 2 steps low-noise
        high_steps = max(1, steps // 2)
        total_steps = steps

        return {
            "71": {
                "class_type": "CLIPLoader",
                "inputs": {
                    "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                    "type": "wan",
                    "device": "default",
                },
                "_meta": {"title": "CLIP Loader (Wan UMT5)"},
            },
            "73": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": "wan_2.1_vae.safetensors",
                },
                "_meta": {"title": "VAE Loader"},
            },
            "75": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
                    "weight_dtype": "default",
                },
                "_meta": {"title": "High Noise UNET"},
            },
            "76": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors",
                    "weight_dtype": "default",
                },
                "_meta": {"title": "Low Noise UNET"},
            },
            "83": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "model": ["75", 0],
                    "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors",
                    "strength_model": 1.0,
                },
                "_meta": {"title": "High Noise 4-Step LoRA"},
            },
            "85": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "model": ["76", 0],
                    "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors",
                    "strength_model": 1.0,
                },
                "_meta": {"title": "Low Noise 4-Step LoRA"},
            },
            "82": {
                "class_type": "ModelSamplingSD3",
                "inputs": {
                    "model": ["83", 0],
                    "shift": shift,
                },
                "_meta": {"title": "Model Sampling High"},
            },
            "86": {
                "class_type": "ModelSamplingSD3",
                "inputs": {
                    "model": ["85", 0],
                    "shift": shift,
                },
                "_meta": {"title": "Model Sampling Low"},
            },
            "74": {
                "class_type": "EmptyHunyuanLatentVideo",
                "inputs": {
                    "width": width,
                    "height": height,
                    "length": length,
                    "batch_size": 1,
                },
                "_meta": {"title": "Empty Latent Video"},
            },
            "89": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["71", 0],
                    "text": prompt,
                },
                "_meta": {"title": "Positive Prompt"},
            },
            "72": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["71", 0],
                    "text": negative_prompt,
                },
                "_meta": {"title": "Negative Prompt"},
            },
            "81": {
                "class_type": "KSamplerAdvanced",
                "inputs": {
                    "model": ["82", 0],
                    "positive": ["89", 0],
                    "negative": ["72", 0],
                    "latent_image": ["74", 0],
                    "add_noise": "enable",
                    "noise_seed": seed,
                    "steps": total_steps,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "start_at_step": 0,
                    "end_at_step": high_steps,
                    "return_with_leftover_noise": "enable",
                },
                "_meta": {"title": "KSampler High Noise (Step 0-2)"},
            },
            "78": {
                "class_type": "KSamplerAdvanced",
                "inputs": {
                    "model": ["86", 0],
                    "positive": ["89", 0],
                    "negative": ["72", 0],
                    "latent_image": ["81", 0],
                    "add_noise": "disable",
                    "noise_seed": seed,
                    "steps": total_steps,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "start_at_step": high_steps,
                    "end_at_step": total_steps,
                    "return_with_leftover_noise": "disable",
                },
                "_meta": {"title": "KSampler Low Noise (Step 2-4)"},
            },
            "87": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["78", 0],
                    "vae": ["73", 0],
                },
                "_meta": {"title": "VAE Decode Latents to Frames"},
            },
            "114": {
                "class_type": "CreateVideo",
                "inputs": {
                    "images": ["87", 0],
                    "fps": fps,
                },
                "_meta": {"title": "Assemble Video Stream"},
            },
            "115": {
                "class_type": "SaveVideo",
                "inputs": {
                    "video": ["114", 0],
                    "filename_prefix": prefix,
                    "format": "auto",
                    "codec": "auto",
                },
                "_meta": {"title": "Save Output MP4 Video"},
            },
        }

    def submit_prompt(self, prompt: dict[str, Any], client_id: str) -> dict[str, Any]:
        """Submit a prompt graph to ComfyUI /prompt endpoint."""
        url = f"{self.base_url}/prompt"
        payload = json.dumps({"prompt": prompt, "client_id": client_id}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            logger.error("ComfyUI prompt submission rejected (%d): %s", e.code, err_body)
            raise RuntimeError(f"ComfyUI /prompt rejected with HTTP {e.code}: {err_body}") from e

    async def stream_progress_and_wait(
        self,
        prompt_id: str,
        client_id: str,
        on_progress: Callable[[str, int, int], None] | None = None,
        timeout: float = 600.0,
    ) -> dict[str, Any]:
        """Stream execution progress over WebSocket until prompt completes."""
        if aiohttp is None:
            raise RuntimeError("aiohttp is required for WebSocket streaming progress.")

        ws_url = f"{self.ws_url}?clientId={client_id}"
        start_time = time.time()
        logger.info("Connecting to WebSocket: %s", ws_url)

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                logger.info("WebSocket connected. Streaming progress for prompt: %s", prompt_id)
                async for msg in ws:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Generation timed out after {timeout} seconds")

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        msg_type = data.get("type")
                        msg_data = data.get("data", {})

                        if msg_type == "status":
                            queue_rem = msg_data.get("status", {}).get("exec_info", {}).get("queue_remaining", 0)
                            logger.debug("Queue remaining: %d", queue_rem)

                        elif msg_type == "execution_start":
                            p_id = msg_data.get("prompt_id")
                            if p_id == prompt_id:
                                logger.info("Execution started for prompt %s", prompt_id)

                        elif msg_type == "progress":
                            node = msg_data.get("node")
                            value = msg_data.get("value", 0)
                            max_val = msg_data.get("max", 0)
                            if on_progress:
                                on_progress(node, value, max_val)
                            else:
                                logger.info("Progress Node %s: %d/%d steps", node, value, max_val)

                        elif msg_type == "executing":
                            node = msg_data.get("node")
                            p_id = msg_data.get("prompt_id")
                            if node is None and (p_id is None or p_id == prompt_id):
                                logger.info("Execution completed for prompt %s!", prompt_id)
                                break
                            elif p_id == prompt_id:
                                logger.info("Executing node ID: %s", node)

                        elif msg_type == "execution_success":
                            p_id = msg_data.get("prompt_id")
                            if p_id == prompt_id:
                                logger.info("Execution succeeded for prompt %s!", prompt_id)
                                break

                        elif msg_type == "execution_error":
                            p_id = msg_data.get("prompt_id")
                            if p_id == prompt_id:
                                err_msg = msg_data.get("exception_message", "Unknown execution error")
                                logger.error("Execution error: %s", err_msg)
                                raise RuntimeError(f"ComfyUI execution error: {err_msg}")

                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        logger.warning("WebSocket closed unexpectedly.")
                        break

        # Fetch completion history
        return self.get_history(prompt_id)

    def download_output_video(
        self,
        history: dict[str, Any],
        prompt_id: str,
        output_dir: Path | str = "results/video",
    ) -> list[Path]:
        """Extract output video files from history entry and download them locally."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        prompt_history = history.get(prompt_id, {})
        outputs = prompt_history.get("outputs", {})
        downloaded: list[Path] = []

        for node_id, node_output in outputs.items():
            # SaveVideo produces "videos", other video nodes may produce "gifs" or "images"
            video_list = node_output.get("videos") or node_output.get("images") or node_output.get("gifs") or []
            for item in video_list:
                filename = item.get("filename")
                subfolder = item.get("subfolder", "")
                type_ = item.get("type", "output")
                if not filename:
                    continue

                view_params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": type_})
                view_url = f"{self.base_url}/view?{view_params}"
                target_path = out_dir / filename

                logger.info("Downloading generated video from %s -> %s", view_url, target_path)
                req = urllib.request.Request(view_url)
                with urllib.request.urlopen(req) as resp, open(target_path, "wb") as f_out:
                    f_out.write(resp.read())

                logger.info("Successfully saved video (%d bytes): %s", target_path.stat().st_size, target_path)
                downloaded.append(target_path)

        return downloaded


def run_test(
    prompt: str = DEFAULT_PROMPT,
    length: int = 17,
    width: int = 640,
    height: int = 640,
    steps: int = 4,
    fps: float = 16.0,
    seed: int | None = None,
    output_dir: str = "results/video",
    wait: bool = True,
    server: str = DEFAULT_SERVER,
) -> dict[str, Any]:
    """Execute end-to-end test run against ComfyUI instance."""
    client = ComfyVideoClient(server=server)

    logger.info("Checking ComfyUI connection at %s...", client.base_url)
    q = client.get_queue()
    running_count = len(q.get("queue_running", []))
    pending_count = len(q.get("queue_pending", []))
    logger.info("ComfyUI status: Running=%d, Pending=%d", running_count, pending_count)

    client_id = f"client_{int(time.time()*1000)}"
    prompt_graph = client.build_wan22_prompt(
        prompt=prompt,
        length=length,
        width=width,
        height=height,
        steps=steps,
        fps=fps,
        seed=seed,
    )

    logger.info("Submitting prompt (Length: %d frames, Resolution: %dx%d)...", length, width, height)
    resp = client.submit_prompt(prompt_graph, client_id=client_id)
    prompt_id = resp.get("prompt_id")
    logger.info("Prompt queued successfully. Prompt ID: %s", prompt_id)

    if not wait:
        return {
            "status": "queued",
            "prompt_id": prompt_id,
            "server": client.base_url,
            "queue": client.get_queue(),
        }

    logger.info("Waiting for execution and streaming progress over WebSocket...")
    history = asyncio.run(client.stream_progress_and_wait(prompt_id, client_id=client_id))

    downloaded = client.download_output_video(history, prompt_id, output_dir=output_dir)
    return {
        "status": "completed",
        "prompt_id": prompt_id,
        "downloaded_files": [str(p) for p in downloaded],
        "output_dir": output_dir,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ComfyUI Wan 2.1 / 2.2 Text-to-Video test client")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Positive text prompt")
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT, help="Negative text prompt")
    parser.add_argument("--length", type=int, default=17, help="Number of frames (e.g. 17 for quick test, 81 for full 5s)")
    parser.add_argument("--width", type=int, default=640, help="Video width (default: 640)")
    parser.add_argument("--height", type=int, default=640, help="Video height (default: 640)")
    parser.add_argument("--steps", type=int, default=4, help="Sampling steps (default: 4 for lightx2v LoRA)")
    parser.add_argument("--fps", type=float, default=16.0, help="Output video frames per second")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output-dir", default="results/video", help="Directory to save output video")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="ComfyUI server address (default: 127.0.0.1:8188)")
    parser.add_argument("--no-wait", action="store_true", help="Queue the prompt and return immediately without waiting")
    parser.add_argument("--status", action="store_true", help="Check queue status and exit")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    client = ComfyVideoClient(server=args.server)

    if args.status:
        q = client.get_queue()
        if args.json:
            print(json.dumps(q, indent=2))
        else:
            print(f"Queue Running ({len(q.get('queue_running', []))}):")
            for item in q.get("queue_running", []):
                print(f"  - ID: {item[1]}")
            print(f"Queue Pending ({len(q.get('queue_pending', []))}):")
            for item in q.get("queue_pending", []):
                print(f"  - ID: {item[1]}")
        return 0

    try:
        result = run_test(
            prompt=args.prompt,
            length=args.length,
            width=args.width,
            height=args.height,
            steps=args.steps,
            fps=args.fps,
            seed=args.seed,
            output_dir=args.output_dir,
            wait=not args.no_wait,
            server=args.server,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== Video Generation Finished ===")
            print(f"Status: {result.get('status')}")
            print(f"Prompt ID: {result.get('prompt_id')}")
            if result.get("downloaded_files"):
                print("Generated video file(s):")
                for f in result["downloaded_files"]:
                    print(f"  => {f}")
        return 0
    except Exception as e:
        logger.exception("Video generation run failed: %s", e)
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
