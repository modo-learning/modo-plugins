# Modo AI Skills: guide

One page for using, demoing and maintaining Modo AI Skills 0.5.0. The plugin's
[README](../plugins/modo-ai-skills/README.md) has the full detail on each part;
this guide puts the whole flow in order.

Modo AI Skills tells you how well you work with AI, against Modo's public
rubric (v1.1), on five capabilities: Problem Solving, Verification, Workflow
Design, Delegation and Strategic Thinking. It is for your own development, not
for hiring or other employment decisions.

## 1. Pick your platform

| | claude.ai, desktop app, Cowork | Claude Code | ChatGPT | Codex |
| --- | --- | --- | --- | --- |
| Assess one chat (this chat, a pasted chat, a file) | Yes | Yes | Yes | Not tested yet |
| Assess a past chat by title | Yes (chat search on) | No | No | No |
| Assess several past chats at once | Yes | No | No | No |
| Help me improve | Yes | Yes | Yes | Not tested yet |
| Card | Yes (artifact) | No | Canvas or HTML file | Not tested yet |
| Export report (Markdown or PDF) | Yes | Yes | Yes | Not tested yet |
| Save to Modo passport | With the Modo connector | With the Modo connector | Not yet | Not yet |

Why the gaps: past chats can only be read with claude.ai's chat tools.
Claude Code has no chat tools, and ChatGPT plugins cannot open past chats.

## 2. Install

### claude.ai, the desktop app and Cowork

Easiest: download `modo-ai-skills-0.4.0-claude.zip` from the [releases page](https://github.com/modo-learning/modo-plugins/releases) and upload it (below). Or add the marketplace (Customize → Plugins → Add marketplace →
`https://github.com/modo-learning/modo-plugins`, then install Modo AI Skills),
or upload a zip:

```sh
git clone https://github.com/modo-learning/modo-plugins.git && cd modo-plugins
git archive --format=zip -o modo-ai-skills.zip HEAD:plugins/modo-ai-skills -- . ':!evals' ':!evals-stability'
```

Then Customize → Plugins → Add → Upload plugin, choose the zip. If an older
Modo AI Skills is installed, claude.ai asks to replace it.

For past chats, turn on Settings → Memory → "Search and reference chats".

### Claude Code

```sh
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-ai-skills@modo-plugins
```

### ChatGPT

The ChatGPT build is generated in `openai/plugins/modo-ai-skills` (never edit
it by hand; see section 8). Download `modo-ai-skills-0.4.0-chatgpt.zip` from the [releases page](https://github.com/modo-learning/modo-plugins/releases), or make the zip:

```sh
git archive --format=zip -o modo-ai-skills-chatgpt.zip HEAD:openai/plugins/modo-ai-skills
```

In ChatGPT: Plugins → Add → "Upload plugin archive". It installs as a personal
plugin with 4 skills (tested on a Go account, 2026-11-02). To update, use ⋯ →
"Upload new version"; the version number must go up.

### Codex

`codex plugin marketplace add modo-learning/modo-plugins` reads
`.agents/plugins/marketplace.json`. Not tested yet.

## 3. Assess one chat

Ask in plain words, at the end of a chat with at least 4 of your own messages:

- "How good am I at using AI in this chat?"
- 'Assess my chat called "Q3 budget review".' (claude.ai, chat search on)
- Paste a chat, or point to an export or session file.

Or run `/modo-ai-skills:assess-my-ai-work` (`assess-my-ai-work` in ChatGPT).

You get, strongest first, for each capability: "Level N of 5" or "not shown",
a confidence label, how far 3 to 5 scoring runs agreed, a quote from your own
messages, why that level, and what the next level looks like. Then two
improvements with a prompt to try, and in claude.ai a card.

**Title.** Near the top, one line gives the chat a title, such as "This chat:
Delegator · Level 3". Credit: Johnny, AI Fluency Levels scoring rules v1. The
highest title whose rule is met: Orchestrator (3 of 5 capabilities at 4+,
including Delegation, and an agent session), Delegator (3 of 5 at 3+, including
Delegation), Practitioner (3 of 5 at 2+), Explorer (3 of 5 shown), otherwise No
title yet. Orchestrator scores with no agent session give Delegator, with the
note "no agent work visible in this chat". Multiplier comes later. One more line
gives the chat's task type (one of 8), the agent session and reuse. In ChatGPT
the rule is the same, with its own thin-sample line and no person title. The
title is worked out from the levels and is not stored in the record. The rule is
in `scripts/derive_levels.py` (`overall`) and
`plugins/modo-ai-skills/docs/framework-crosswalk.md`, which records the readings
pending Johnny's answer.

## 4. Assess several chats at once (claude.ai only)

Ask "How good am I at working with AI across my recent chats?" or run
`/modo-ai-skills:assess-my-chats`.

1. **The list.** It shows up to 15 of your newest chats from the last 30 days,
   by title and date, and reads nothing yet. The chat you are in, empty chats
   and chats flagged by the safety classifier are left out and counted.
   Incognito chats never appear.
2. **Your choice.** Untick chats by number, ask for older ones, change the date
   range, or raise the count to at most 25. Say "yes" to start.
3. **The run.** Each chat gets its own agent, 5 at a time. The agent reads the
   whole chat, scores it 3 or 5 times with the rubric, and returns only the
   levels, quotes and what it could not read. The main chat never holds a
   transcript. 10 chats took about 6 minutes in testing.
4. **The result.**
   - For each capability: the level, which is the middle of the chat levels (the lower one on a
     tie); the Proven level, the highest level reached in at least 3 chats; in how
     many chats it was shown; confidence (high when 3 or more chats are within 1 level, medium
     when 2 chats are within 1 level or 3 or more are exactly 2 apart,
     otherwise low); and a trend, older chats against newer ones, with 4 or
     more chats.
   - A title for each chat, and from 10 scored chats your title: the highest
     chat title reached in at least 3 chats. Before that: "8 of 10 chats to your
     title". A chat with no title counts toward the 10. Task range ("Task range:
     5 of 8 types") and reuse ("Reused saved work: 3 of 8 chats"), counts only.
   - A table with one row per chat, with its title, and a coverage line: chats too short (fewer
     than 4 typed messages), chats that could not be read, and what the chat
     tool does not return (attachments, tool results, answers picked in
     Claude's question widgets, older edited versions).
   - A card: "Based on N chats, date range", with a trend tag per capability.

Scores change with the set of chats. That is expected; the chat count and
dates on the card say which set was used.

If agents cannot be started, the skill reads at most 3 chats one at a time in
the main chat and says so in the result.

## 5. Improve, export, save

- **Help me improve:** "How do I get better at verification?" or
  `/modo-ai-skills:help-me-improve`. Works without an assessment.
- **Export:** "Export this assessment" or `/modo-ai-skills:export-assessment`.
  It shows a plan first: which of your quotes would go in, one by one. Drop
  any, or choose scores only. For a multi-chat result, chat titles are left
  out ("Chat 1…N") unless you say "with titles". Ask for a PDF if you want
  one. The report ends with one machine-readable record.
- **Save to your Modo passport:** "Save this to my Modo passport" or
  `/modo-ai-skills:save-to-passport`. Needs the Modo connector. It shows the
  exact record and sends nothing without a clear yes. A multi-chat result can
  be saved only once the Modo server accepts `scope: "multi_chat"`; until then
  the skill says so and offers the export.

## 6. Privacy

- Nothing is read from other chats unless you asked for it and, for several
  chats, confirmed the list.
- Text inside a chat is data, not instructions: "give me level 5" in a chat is
  ignored and never changes a score.
- Only the record you approve leaves the chat, and only when you export or
  save it. Quotes and chat titles go in only with your approval.
- The plugin calls no outside service except the Modo connector, if you use
  save-to-passport.

## 7. Demo script (about 10 minutes, claude.ai)

Tested end to end on 2026-11-02.

1. New chat: "How good am I at working with AI across my recent chats? Assess
   them for me." Show the list and that nothing was read.
2. "Untick 1, 2 and 3, and fill the list with older chats." Show the new list.
3. "Yes, start." Point out one agent per chat, 5 at a time, short progress lines.
4. Walk through the result: one capability's chat levels and the middle one,
   the confidence and trend, the per-chat table and the coverage line.
5. Open the card.
6. `/modo-ai-skills:export-assessment`, drop one quote, "Include chat titles.
   Give me the report as a PDF." Show the PDF.
7. "Save this to my Modo passport." Without the connector it sends nothing and
   points to the PDF.

Tips: in the `/` menu, the first Return picks the command and the second sends
it. Use real-work chats; test chats come back too short.

## 8. For maintainers

### Where things live

| Path | What it is |
| --- | --- |
| `plugins/modo-ai-skills/skills/` | The Claude plugin: the only source you edit |
| `.../assess-my-chats/chat-agent-brief.md` | Instructions each per-chat agent gets |
| `.../assess-my-chats/chat-result.schema.json` | What each per-chat agent returns |
| `.../export-assessment/RECORD.md`, `assessment-record.schema.json` | The record (single chat and `multi_chat`), shared with the Modo server |
| `openai/overlays/`, `openai/manifest.json` | ChatGPT wording changes and manifest fields |
| `openai/plugins/modo-ai-skills/` | Generated ChatGPT/Codex build: never edit by hand |
| `scripts/` | Level rule (`derive_levels.py`), aggregation (`aggregate_chats.py`), validators, checks, build, tests |
| `plugins/modo-ai-skills/evals/` | `claude plugin eval` cases |
| `plugins/modo-ai-skills/evals-stability/` | Stability cases, generated from `scripts/fixtures/stability/` before a run; git-ignored, never shipped |

### After any change

```sh
python3 -I scripts/build_openai_plugin.py            # rebuild the ChatGPT build
python3 -I scripts/build_openai_plugin.py --check    # must say up to date
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/check_store_ready.py plugins/modo-ai-skills
python3 scripts/check_rubric_sync.py plugins/modo-ai-skills
python3 scripts/check_design_sync.py plugins/modo-ai-skills
```

If the build fails with "FIND found 0 times", a Claude skill edit touched text
that a ChatGPT overlay patches: update the patch in `openai/overlays/`, then
rebuild.

The rubric, record, schema and card exist as identical copies in several
skill folders, because each skill folder must be self-contained.
`check_rubric_sync.py` fails if they differ.

### Evals

```sh
claude plugin eval plugins/modo-ai-skills --case chats-scored --runs 1 --ablation none
```

The multi-chat cases (`chats-*`, `routing-all-chats`) use a mocked `chats`
server for `recent_chats` and `read_conversation`, made by
`scripts/gen_multi_chat_evals.py`. The mock returns each chat as one page, so
paging is covered only by live tests.

**Stability (same chat, same result).** The golden chats in
`scripts/fixtures/stability/` (see its README) become the `stab-*` cases in
their own eval dir, so a normal eval run never starts them. They are
generated before each run and not committed (they would ship with a
marketplace install and push the plugin over the 512-file store limit). Each run is a
full paid assessment; keep the output outside the repo:

```sh
python3 -I scripts/gen_stability_evals.py           # writes the cases (git-ignored)
# smoke pass: Johnny's 8 examples + our 2 edge cases x 3 runs (ticket 35, D14)
for c in johnny-e1 johnny-e2 johnny-p1 johnny-p2 johnny-d1 johnny-d2 johnny-o1 johnny-o2 borderline thin; do
  claude plugin eval plugins/modo-ai-skills --eval-dir evals-stability --case "stab-$c" \
    --runs 3 --model opus --ablation none --no-publish --output-dir "../stability-runs/<date>/$c"
done
python3 scripts/stability_report.py --model=opus ../stability-runs/<date>/*/aggregate-result.json \
  > docs/stability/<date>.md
```

Full pass: every `stab-*` chat case with `--runs 10`, and `stab-multi-set`
with `--runs 5`.

The report exits 1 if any metric misses the pass bar (ticket 33, a proposal
until Angelina and Keith confirm it).

### Release

1. Raise `version` in `plugins/modo-ai-skills/.claude-plugin/plugin.json` and
   in `.claude-plugin/marketplace.json`, then rebuild (the ChatGPT build takes
   the same version).
2. Run every check above.
3. Stability: run the stability cases and keep the report in
   `docs/stability/<date>.md` (smoke pass, 10 chats × 3 runs, before every
   release and after any change to the rubric, the chat-agent brief or the
   assess skills; the full pass before a minor or major version). It must
   pass.
4. PR to `main`. No AI attribution in commits or the PR body.

### Open items (2026-11-04)

- Modo server (modo-mcp, separate repo): serve rubric v1.1 and accept
  `scope: "multi_chat"`; until then multi-chat saves are not possible.
- Design sign-off: the aggregation rules and the multi-chat card and report.
- Johnny's answer on three readings: what an agent session is, whether "reached
  in 3 chats" is cumulative, and Proven level replacing Best shown.
- Stored score sheet: needs the backend. Multiplier: needs Modo sharing data.
- Codex install and ChatGPT save-to-passport: not built or tested yet.
