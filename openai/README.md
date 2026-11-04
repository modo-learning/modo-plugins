# Modo AI Skills for ChatGPT and Codex

`plugins/modo-ai-skills/` (the Claude plugin) is the only source that is edited.
`openai/plugins/modo-ai-skills/` is **generated** from it: never edit it by hand.

| Path | What it is |
| --- | --- |
| `openai/manifest.json` | OpenAI-only manifest fields (description, links, `extensions.com.openai.interface`). Name, version, author and license come from the Claude manifest. |
| `openai/overlays/<skill>/<file>.patch` | FIND/REPLACE blocks with the ChatGPT wording. Each FIND must match the source exactly once, so an edit to the Claude skill that touches patched text fails the build. |
| `openai/plugins/modo-ai-skills/` | The built plugin: portable `plugin.json`, `skills/`, `LICENSE`. |
| `.agents/plugins/marketplace.json` | The marketplace entry partner admins import from this repo. |

## Build

```sh
python3 -I scripts/build_openai_plugin.py          # rebuild after any change
python3 -I scripts/build_openai_plugin.py --check  # fails if the build is stale
python3 -I scripts/test_build_openai_plugin.py
```

## What differs from the Claude plugin (v1)

- Ships assess-my-ai-work, help-me-improve, export-assessment and modo-design.
  save-to-passport and the Modo connector come later.
- Assesses this chat or a pasted chat; ChatGPT plugins can't open past chats.
- The one-chat title rule is the same (Johnny's scoring rules v1). There is no
  person title, Proven level or task range, and the thin-sample line has its own
  wording. The build leaves out everything between MODO-PERSON markers.
- The card is shown in a canvas if one is available, otherwise offered as a
  downloadable HTML file, otherwise left out (text result only).
- The PDF is made with ChatGPT's file or code tool; without one, the report is
  given as Markdown with a "Print, then Save as PDF" hint.
- The label reads "Self-assessment by ChatGPT using Modo rubric v1.1 — not verified."
- The rubric, `RECORD.md` and the record schema are byte-identical to the
  Claude plugin's (shared with the modo-mcp server).
