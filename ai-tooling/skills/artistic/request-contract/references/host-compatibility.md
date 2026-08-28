---
doc_kind: supporting
canonical_id: artistic-request-host-compatibility
purpose: [process, interoperability]
rank: medium
topics: [agent-skills, cursor, claude-code, antigravity, capability-negotiation, artistic-workflows]
rag_keywords: [Cursor, Claude Code, Antigravity, Agent Skills, .agents/skills, .claude/skills, graphical, media, browser, cloud, sandbox, portability]
---

# Artistic request host compatibility

This reference records observed host behavior that can affect a portable artistic request workflow. It is not a provider guarantee. Re-probe the active host and surface before execution; the request contract remains authoritative.

## Stable portability rules

The [Agent Skills specification](https://agentskills.io/specification) requires a directory with `SKILL.md`, YAML `name`, and `description`; optional fields and tool permissions vary. Use ordinary Markdown, relative resource links, explicit capability probes, and evidence reports. Avoid client-only interpolation, shell-injection syntax, hidden state, or assumptions that a script, image viewer, browser, renderer, or persistent artifact store exists.

Project-scoped skills are the safest portability boundary for a checked-out repository. A cloud or sandbox agent may not have user-level files or the same filesystem, so require authorized attachment/upload and record what was actually available. Name the active host, surface, model/tool version when exposed, and session/workspace scope in the handoff.

## Host and surface differences

| Host class | Officially documented behavior relevant to this skill | Mitigation in the contract workflow |
| --- | --- | --- |
| Cursor Agent / CLI / Cloud Agent | Cursor documents project and user skill locations, compatibility loading from common skill directories, file/image reading, browser control, and image generation in Agent; it also notes that user-level skills are not copied to Cloud Agents or remote workers. See [Cursor Agent Skills](https://cursor.com/docs/skills) and [Agent overview](https://cursor.com/docs/agent/overview). | Prefer a project-scoped skill. Probe `visual_input`, `visual_output`, `browser`, `artifact_persistence`, and `image_generation` for the current surface. Verify the saved artifact path and inspect the delivered file, not the chat preview alone. |
| Claude Code local / cloud / Cowork | Claude Code loads project skills from `.claude/skills/`, supports explicit or model-driven activation, and distinguishes local, cloud, and Cowork behavior. Its documented `!` command injection and `@` references have session-specific limits. See [Claude Code skills](https://code.claude.com/docs/en/skills). | Use the plain contract and explicit file reads. Do not depend on `!` commands, `@` attachment semantics, or personal skills. Require the host to report whether the artifact, references, and any visual inspection actually loaded. |
| Google Antigravity Agent Manager / IDE / CLI | Google’s skills codelab documents project skills under `<project-root>/.agents/skills/` and a separate global scope; other Antigravity surfaces and browser/media capabilities can differ. See [Authoring Google Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills?hl=en) and [Getting Started with Google Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity). | Place the portable skill in a project-visible location when installing for Antigravity. Record the exact surface. Never infer that IDE/Agent Manager browser or artifact features exist in CLI; mark absent or unknown capabilities as a hold for any required visual check. |
| Coding agent without media tools | Text/file/shell access may exist without image/audio/video generation or pixel-level review. | Prepare the contract, run deterministic metadata checks where possible, and hand off to a graphical/media-capable tool with the ledger and authorized references. Do not pretend that a filename or provider text response verifies pixels. |
| Graphical or media-capable tool | Generation, editing, preview, OCR, and media inspection may be available, but exact support for text, references, alpha, color, audio, 3D, or provenance varies by tool and mode. | Probe each capability rather than inferring it from the product label. Test the actual output at delivery condition, preserve variants only when authorized, and record unsupported or stripped provenance as a limitation. |

## Probe record

Use this compact record before an execution or review:

```text
host/product/surface/version: [reported value or unknown]
workspace scope: [project | user | cloud | sandbox | external]
inputs: [text | images | audio | video | 3d | references; loaded?]
actions: [generate | edit | inspect | OCR | transcribe | render | browser/device preview]
output: [persisted path/URI | preview only | unavailable]
checks: [metadata | pixels/frames | text | audio | accessibility | package fixity]
provenance: [exported | partial | unavailable]
approval/permissions: [prompted, granted, denied, or unknown]
```

If a host cannot answer a field, preserve `unknown`; do not fill it from a vendor name, model reputation, file extension, or tool description.
