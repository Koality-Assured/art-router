# Change history — 2026 Q4

Entries newest first. Append via `python scripts/change-history/append_change_history.py` only.

## Entries







### 2026-10-11 — Add local LLM prompt evaluator pipeline and --refine-llm integration

- **Requesting user:** Robbie
- **AI agent:** artistic-production
- **User request:** Hm, perhaps we add a methodology for it to automatically take a prompt and uses a local model to evaluate and adjust that prompt and manage the tags and all that?
- **Summary:**
  - Built prompt_evaluator.py connecting local LLM (Ollama/LM Studio/local OpenAI endpoint) to Danbooru 8-slot decomposition
  - Integrated graceful fallback and unit tests with 100% pass rate
  - Added --refine-llm to test_comfy_video and global prompt-refine CLI shortcut

### 2026-10-11 — Incorporate Danbooru tag ontology, prompt ordering standards, catalogs, and compiler into art-router

- **Requesting user:** Robbie
- **AI agent:** artistic-production
- **User request:** Let's figure out incorporating tag groups, do deep research here and get it added into the art-router. https://danbooru.donmai.us/wiki_pages/tag_groups
- **Summary:**
  - Conducted deep research into Danbooru tag groups hierarchy, 5 native category IDs, and REST API endpoints
  - Authored docs/standards/danbooru-tag-ontology.md and docs/standards/prompt-token-ordering.md defining 8-slot canonical sequence
  - Built machine-readable catalogs under references/prompt-engineering/catalogs/danbooru-tags/ (categories.json, tag-groups.json, model-dialects.json)
  - Created scripts/tools/compile_prompt.py CLI and harness prompt compile with 100% test coverage
  - Created danbooru-tagging Schema V2 skill and regenerated routing index

### 2026-10-11 — Add media-history-purge skill and harness video purge command

- **Requesting user:** Robbie
- **AI agent:** artistic-production
- **User request:** Store a skill for cleanup that does all this in the art router then.
- **Summary:**
  - Created media-history-purge Schema V2 skill in art-router
  - Created purge_media_history tool with ComfyUI memory, ffmpeg metadata strip, artifact deletion, and shell history scrub
  - Integrated harness video purge CLI command and regenerated routing dispatch

### 2026-10-11 — Integrate ComfyUI Wan 2.2 video generation into art-router harness

- **Requesting user:** Distasteful
- **AI agent:** antigravity
- **User request:** Make sure ComfyUI Wan 2.2 video generation is integrated into art harness
- **Summary:**
  - Ported ComfyVideoClient scripts/tools/test_comfy_video.py with WebSocket progress streaming and auto MP4 download
  - Integrated harness video generate/status/models command into art-router harness.py
  - Added stdio MCP server scripts/tools/comfy_video_mcp_server.py exposing video tools to coding agents
  - Created video-generation skill in ai-tooling/skills/artistic/video-generation/SKILL.md with Schema V2 validation
  - Added test_comfy_video_integration.py and supporting/comfyui/ documentation

### 2026-10-08 — Summarize art bundle routes in text output

- **Requesting user:** Robbie
- **AI agent:** Codex
- **User request:** Fix the schema 1.3 art-router text report so bundle cases show their routes.
- **Summary:**
  - Derive a stable route summary from 1.3 components while preserving legacy case.medium labels.
  - Add regression coverage for 1.3 summaries and 1.0–1.2 formatting.

### 2026-10-08 — Align art manifest 1.3 component shape

- **Requesting user:** Robbie
- **AI agent:** Codex
- **User request:** Correct schema 1.3 art request and bundle fields to match the normative component shape.
- **Summary:**
  - Use route, nested asset.type, and primary/supporting roles; reject old 1.3 field names and adjacent role.
  - Add a prose-conforming mixed-media fixture and keep 1.0–1.2 manifests compatible.

### 2026-10-08 — Expand art router representations

- **Requesting user:** Robbie
- **AI agent:** Codex
- **User request:** Expand the art router with validated representation coverage, production guidance, official references, and sample gallery entries.
- **Summary:**
  - Add registry-driven routing and schema 1.3 mixed-media validation while preserving manifest 1.0–1.2.
  - Add a write-capable production workflow, focused standards captures, and package-validated sample metadata.

### 2026-10-07 — Allow factual employer-mark identification

- **Requesting user:** portfolio owner
- **AI agent:** Cursor agent
- **User request:** Represent résumé-style employer marks as factual identifiers without asserting a separate per-logo written license.
- **Summary:**
  - Added a factual-identification source status for organization marks with identification-only scope. Kept publisher cinematics gated on permission evidence and clarified that source context is not a license or legal opinion.

### 2026-10-07 — Third-party mark and publisher embed contract

- **Requesting user:** Portfolio owner
- **AI agent:** Codex
- **User request:** Extend the Art router for company marks and cinematic embeds.
- **Summary:**
  - Added schema 1.2 with per-source usage evidence, kind-specific scopes, and constrained YouTube embed controls.
  - Added a synthetic fixture, pass/hold tests, routing guidance, and source-grounded policy notes.

