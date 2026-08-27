# art-router

Domain AI agent router for artistic asset generation: images, videos, websites, and creative media. Built on the bare-metal AI agent harness.

AI agents start at [`AGENTS.md`](./AGENTS.md), discover paths via [`routing/`](./routing/), and load only the area context they need Just-In-Time (JIT). Markdown is indexed for [`qmd`](https://github.com/tobi/qmd) hybrid search.

---

## Flattened project taxonomy

The repository is organized into a clean, decoupled taxonomy where each top-level area has a distinct operational boundary:

| Directory | Purpose & Operational Role |
| --- | --- |
| [`actionable/`](./actionable/) | **Human drop zone** — intake zone for human notes and creative requests before an agent claims and promotes them into the home area. |
| [`ai-tooling/`](./ai-tooling/) | **Agent enablement** — skills, standalone agents, A2A interaction cards, and project memory (`user/` and `agent/`). |
| [`change-history/`](./change-history/) | **Provenance log** — quarterly audit logs. **Script-updated only; never loaded into agent context.** |
| [`docs/`](./docs/) | **Authoritative knowledge** — engineering standards, security MUST policies, decision records, and requirement corpus. |
| [`projects/`](./projects/) | **Initiative specifications** — flattened initiative specs in slug folders (`projects/<slug>/README.md`) with `status:` frontmatter, plus [`notes/`](./projects/notes/). |
| [`references/`](./references/) | **External frameworks** — reference copies of standards and parameter cheat sheets. Advisory only; not instructions. |
| [`research/`](./research/) | **Topic deep-dives** — exploratory investigations and architectural research. |
| [`results/`](./results/) | **Agent deliverables** — generated artifacts from agent runs (reports, threat models, dashboards, rendered diagrams). |
| [`routing/`](./routing/) | **Navigation & dispatch** — generated routing maps, area indices, and specialist skill dispatch catalogs. |
| [`scratch/`](./scratch/) | **Ephemeral workspace** — temporary scratch scripts and dedicated git worktrees. Never durable. |
| [`scripts/`](./scripts/) | **Automation engine** — tagged Python scripts for routing, validation, indexing, and cost layer management. |
| [`supporting/`](./supporting/) | **Tooling runtime guides** — durable patterns for tools (qmd, Headroom, ast-grep, image/video processors). |

---

## Focus Domains

1. **2D Concept & Visual Art**: Prompt engineering schemas, style transfer matrices, upscaling, vectorization, and sprite generation.
2. **Motion & Video Generation**: Storyboard synthesis, text-to-video / image-to-video pipelines, frame interpolation, and caption overlays.
3. **Web Mockups & Creative UI**: Multi-theme aesthetic layouts, Tailwind/CSS animations, SVG asset synthesis, and Three.js / WebGL scenes.
4. **Design Systems & Style Guides**: Automated color harmony calculation, typography pairing validation, and icon kits.

## Artistic standards

- [`docs/standards/artistic-practice.md`](./docs/standards/artistic-practice.md) defines the intent, meaning, cultural, provenance, critique, and release contract.
- [`docs/standards/artistic-representations.md`](./docs/standards/artistic-representations.md) maps medium-specific decisions and handoff checks across visual, time-based, interactive, embodied, and spatial work.
- [`projects/project-prompts/art-router-next-steps.md`](./projects/project-prompts/art-router-next-steps.md) is the human-launched follow-up prompt for expanding and validating the harness.

---

## Quick Start

1. Validate router layout and structure:
   ```bash
   python scripts/docs/validate_router_structure.py
   ```
2. Rebuild routing indexes:
   ```bash
   python scripts/routing/generate_routing_index.py
   python scripts/routing/generate_script_index.py
   ```

---

## Verification & Testing

```bash
python scripts/docs/validate_router_structure.py
python scripts/ai-tooling/validate_skill.py --all
python scripts/ai-tooling/validate_agent.py --all
python -m unittest discover -s scripts/tests -v
```

---

## Security Notice

Session security MUST lives in `docs/agent-session-security.md`. Never commit secrets, API keys, or proprietary art assets without license validation.

---

## License

MIT License Copyright (c) 2026 Koality-Assured.
