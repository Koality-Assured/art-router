---
schema_version: "2.0.0"
name: media-history-purge
description: >-
  Purge ComfyUI in-memory execution history, losslessly strip embedded prompt metadata
  from generated MP4/WEBM videos, delete local media artifacts, and scrub shell command history.
  Use when privacy, prompt confidentiality, or local media cleanup is requested after generation.
owner_agent: artistic-production
rank: high
isolation: mutate
on_failure: abort_and_rollback
prerequisites:
  - python
  - ffmpeg
dependencies:
  required_skills:
    - isolate-work
  delegated_skills: []
  in_session_skills:
    - evidence-validation
contracts:
  inputs:
    - Purge targets (--all, --comfy-history, --strip-metadata, --delete-videos, --shell-history), optional ComfyUI server address, and dry-run flag
  outputs:
    - Summary of cleared queue history, stripped video file list, deleted artifact count, and scrubbed shell history count
---

# Media History Purge

## When to use

Use when privacy, prompt confidentiality, or media cleanup is required after generating local images or videos. Common scenarios include:
- Purging ComfyUI's in-memory execution history (`POST /history` with `{"clear": true}`).
- Losslessly stripping embedded prompt graphs, seeds, and workflow JSON from generated MP4/WEBM files via ffmpeg without re-encoding.
- Deleting generated media files from `results/video/` and ComfyUI `output/` directories.
- Scrubbing command-line history containing sensitive prompt text from PowerShell's `ConsoleHost_history.txt`.

## When not to use

Do not use during active media generation jobs. Do not use for deleting trained model weights, checkpoints, or LoRAs. For workspace or worktree teardown, use [`scratch-cleanup`](../../meta/scratch-cleanup/SKILL.md) and [`isolate-work`](../../meta/isolate-work/SKILL.md).

## Criticality

High. Protects operator privacy and prevents confidential prompt engineering, intellectual property, or draft media artifacts from persisting unmanaged or leaking into downstream repos and distribution channels.

## Source of truth

- [`scripts/tools/purge_media_history.py`](../../../../scripts/tools/purge_media_history.py) provides the programmatic engine and CLI for all purge operations.
- [`scripts/cli/harness.py`](../../../../scripts/cli/harness.py) provides the unified control-plane integration via `harness video purge`.
- [`supporting/comfyui/README.md`](../../../../supporting/comfyui/README.md) documents ComfyUI REST endpoints, memory model, and socket behavior.

## Isolation

`mutate`. All purge actions that delete files, clear memory, or rewrite history modify state. Always preview with `--dry-run` before applying destructive deletions.

## How to use

1. Preview what would be purged across all targets:
   ```powershell
   python scripts/cli/harness.py video purge --all --dry-run
   ```

2. Clear ComfyUI in-memory generation queue only:
   ```powershell
   python scripts/cli/harness.py video purge --comfy-history
   ```

3. Strip embedded metadata from videos without re-encoding (keeps original video stream):
   ```powershell
   python scripts/cli/harness.py video purge --strip-metadata
   ```

4. Delete generated video files from workspace and ComfyUI output:
   ```powershell
   python scripts/cli/harness.py video purge --delete-videos
   ```

5. Perform complete purge of memory, videos, metadata, and shell history:
   ```powershell
   python scripts/cli/harness.py video purge --all --shell-history
   ```

## Dry run

Validate the skill and simulate the purge pipeline without mutating any state:

```powershell
python scripts/ai-tooling/validate_skill.py --skill media-history-purge --dry-run
python scripts/cli/harness.py video purge --all --dry-run
```

## Security

Inherits Critical cost layers: qmd for discovery; ast-grep for structured files; Headroom for bulky tool output. Skills cannot waive root `AGENTS.md`.

- **Metadata sanitization**: ComfyUI embeds the complete prompt graph and execution parameters into MP4 `moov` atoms. Ffmpeg `-map_metadata -1 -c copy` removes this data losslessly without quality degradation.
- **In-memory clearance**: ComfyUI stores prompt history in RAM only (`PromptServer.instance.history`). Calling `/history` with `clear: true` resets this map to `{}`.
- **Shell history**: When prompts are passed as CLI arguments, they may be written to PowerShell's persistent history file. The purge tool scrubs only lines matching generation commands, preserving unrelated history.
- Never log or transmit purged prompts to remote services or third-party endpoints.

## Completion gates

- ComfyUI in-memory history verified cleared (`{}`) if requested.
- Targeted video files verified free of embedded metadata (or deleted if requested).
- Unit test suite passes cleanly:
  ```powershell
  pytest scripts/tests/test_purge_media_history.py
  ```
