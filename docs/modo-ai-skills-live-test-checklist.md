# Modo AI Skills: manual live-test checklist (ticket 07)

Manual checks of v0.1.0 in the three apps, before release. The eval suite
covers most behaviour with synthetic chats; this checklist covers what it
can't: the real apps, real past-chat tools, the card, the Save skill card and
real file creation. The named-past-chat lookup by exact title has never run
against real past-chat tools (the eval environment has none), so section 3c
is the most important.

For each row, mark each app column Pass, Fail or n/a, and write what you saw
in Notes (paste the opening line or the failing sentence). "CC" is Claude
Code, "Chat" is claude.ai chat (web or desktop), "Cowork" is a Cowork task.

## 1. Install from the local branch, without pushing

### Claude Code

Two documented ways; both read the files straight from your working copy.

- **One session, nothing installed** (simplest):
  `claude --plugin-dir <repo>/plugins/modo-ai-skills`
  Source: "Claude Code: run `claude --plugin-dir ./expense-reports` to start a
  session with the plugin loaded from your working copy"
  (https://claude.com/docs/plugins/build#test-the-plugin-on-each-surface).
- **As a local marketplace**:
  `claude plugin marketplace add <repo>` (absolute path, or a relative path
  starting with `./`), then `claude plugin install modo-ai-skills@modo-plugins`.
  Source: "Local directory or file: a relative or absolute path to a directory
  that holds `.claude-plugin/marketplace.json`"
  (https://code.claude.com/docs/en/plugins/install#add-a-marketplace). Plugins
  from a marketplace added from a local path are loaded in place and not
  pinned by `version`; edits apply at the next session start or after
  `/reload-plugins`
  (https://code.claude.com/docs/en/plugins/manifest-reference#version,
  https://code.claude.com/docs/en/plugin-marketplaces#test-an-edit-to-a-plugin).
  Check `claude plugin marketplace list` first: if `modo-plugins` is already
  registered from GitHub (for Task Finder), the local one has the same name,
  so use `--plugin-dir` instead, or remove the GitHub one first (removing a
  marketplace uninstalls its plugins, Task Finder included).

### claude.ai chat and Cowork

**Add marketplace** needs a Git repository URL. Per the docs, for a
marketplace you add yourself "GitHub and GitHub Enterprise repositories work,
and so do public GitLab and Bitbucket repositories"; there is no local-path
option (https://claude.com/docs/plugins/overview#find-and-add-a-plugin,
https://claude.com/docs/plugins/platform-support#compare-installation-sync-and-admin-controls).
Testing through the marketplace in claude.ai and Cowork must wait until the
branch is pushed.

Without pushing, the docs give one other way: **Add > Upload plugin** with a
zip of the plugin folder, uploaded to your own account
(https://claude.com/docs/plugins/build#test-the-plugin-on-each-surface). It
is your choice whether to upload the files to your claude.ai account; this
checklist doesn't assume it. If you do:

1. Zip the plugin folder outside the repo (zips are git-ignored anyway), for
   example:
   `cd <repo>/plugins && zip -r ~/Desktop/modo-ai-skills.zip modo-ai-skills -x '*/evals/*' '*.DS_Store'`
   (the evals are not needed to run the plugin; the archive must hold one
   `.claude-plugin/plugin.json` at its root or inside one top-level folder).
2. claude.ai > Customize > Plugins > Add > Upload plugin, select the zip.
3. Open a new chat and ask which skills it has from plugins: expect
   assess-my-ai-work, export-assessment, help-me-improve.

Notes on the upload route: an uploaded plugin is saved to your account, so
it also shows up in Claude Code as `modo-ai-skills@synced` at the next
session start (https://code.claude.com/docs/en/plugins/install#plugins-from-your-claudeai-account).
Don't load it there twice with `--plugin-dir` in the same session. How an
uploaded plugin is updated after an edit is not specified; remove it and
upload again. Remove it after testing (Customize > Plugins > the plugin's menu
> Remove).

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 1.1 | Plugin installs; the three skills are listed | | | | |
| 1.2 | `/` menu shows `modo-ai-skills:` skills with the exact names | | | | |
| 1.3 | Task Finder still works (run it once) | | | | |

## 2. Before you start

- Prepare one real chat with at least 6 messages from you in which you check
  Claude's work and hand over a task (gives levels, a quote and confidence).
- Prepare one chat with only 2 or 3 messages from you (too short).
- In the Claude app, give two past chats a unique, exact title, for example
  "Modo test alpha", and two more chats the same title, "Modo test twin".
  Turn on Settings > Memory > "Search and reference chats" for the past-chat
  rows.
- Get a Claude data export `conversations.json` (or use
  `plugins/modo-ai-skills/evals/export-file/resources/` fixtures) and one
  Claude Code session `.jsonl` file you are happy to have read.
- Keep an eye on the tool calls in each run: a run must never open, list or
  search anything other than the chat or file you named.

## 3. Chat sources

### 3a. The current chat

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 3a.1 | In the prepared chat, "how good am I at using AI?" triggers the assessment | | | | |
| 3a.2 | Opening line names "this chat" and the message count | | | | |
| 3a.3 | No other chat or file is read (tool calls) | | | | |
| 3a.4 | "Assess all my chats" says it assesses one chat at a time, then assesses this one only | | | | |
| 3a.5 | Too-short chat: "too short to judge", count and minimum of 4, no scores, no card, label last | | | | |

### 3b. Pasted text

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 3b.1 | Pasted chat with "You:"/"Claude:" labels is assessed; opening line "the chat you pasted" | | | | |
| 3b.2 | Pasted text with unclear speakers: asks one short question, no scores | | | | |

### 3c. A named past chat (exact title only, untested path)

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 3c.1 | `assess my chat "Modo test alpha"`: opens that one chat; opening line `your chat "Modo test alpha" (<date>)` | | | n/a | |
| 3c.2 | Note which tool was used (open by title, or one search) and how many calls | | | n/a | |
| 3c.3 | If it was a search: only one search, with the exact title as the query; no second search with other words | | | n/a | |
| 3c.4 | The reply never names, quotes or describes any other search result | | | n/a | |
| 3c.5 | `assess my chat "Modo test twin"`: asks "which one?", listing only the two twins (title and date), no scores | | | n/a | |
| 3c.6 | A title that doesn't exist: "found no chat with that name", nothing else from the search, offers paste or export file | | | n/a | |
| 3c.7 | A topic instead of a title ("my chat about the budget"): does not browse by topic; either an exact-title match or "no chat with that name" | | | n/a | |
| 3c.8 | Claude Code: "can't open past chats here", offers paste, export file, or run it in that chat | n/a | n/a | | |
| 3c.9 | Chat search turned off: says it can't open past chats here (or no match), never guesses | | | n/a | |

### 3d. A chat export file

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 3d.1 | Path to an export with several chats, one named: assesses only that chat; opening line with title and date | | | | |
| 3d.2 | Same file, no chat named: asks "which one?" with titles and dates | | | | |
| 3d.3 | Wrong path: says it can't read it and asks for the path or the chat pasted; no search for the file | | | | |
| 3d.4 | A real current Claude data export parses (the format was only checked against a fixture) | | | | |

### 3e. A Claude Code session file

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 3e.1 | Path to a `.jsonl`: opening line "the Claude Code session file <name>"; count excludes tool results | n/a | | | |
| 3e.2 | No quote comes from a tool result line | n/a | | | |
| 3e.3 | In no other run does it mention or offer session files or coding-tool logs | | | | |

## 4. The result

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 4.1 | Five blocks in rubric order, "Level N of 5 (confidence: ...)", evidence quotes, next level | | | | |
| 4.2 | Every quote is word for word from your own messages, under 240 characters | | | | |
| 4.3 | A capability with nothing on it is "Not shown in this chat", not level 1 | | | | |
| 4.4 | No score out of 100, no "verified"/"certified"/badges/comparisons | | | | |
| 4.5 | Last line exactly "Self-assessment by Claude using Modo rubric v1 — not verified." | | | | |
| 4.6 | Export sentence present (offer, not a question) | | | | |

## 5. The card

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 5.1 | A card appears beside the chat; text says "I also made a card of this result." | | | n/a | |
| 5.2 | Card matches the text: same levels, confidence, quotes copied exactly | | | n/a | |
| 5.3 | "Not shown" capability: empty ring, "Not shown", no zero | | | n/a | |
| 5.4 | Label at the bottom of the card; title "AI capability card" | | | n/a | |
| 5.5 | Reads well in light and dark mode | | | n/a | |
| 5.6 | No card and no card sentence in Claude Code | n/a | n/a | | |
| 5.7 | No card for too-short, "which one?", can't-open or no-match messages | | | | |

## 6. Improvements and the Save skill card

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 6.1 | Two weakest shown capabilities (ties: higher confidence first, then rubric order); never a not-shown one | | | | |
| 6.2 | Each has a technique traceable to the rubric and a paste-ready prompt using your subject | | | | |
| 6.3 | Ends with one offer to make a reusable skill, says nothing is saved unless you choose | | | | |
| 6.4 | "Yes": a Save skill card appears (Chat/Cowork); you save or dismiss it | | | n/a | |
| 6.5 | "Yes" in Claude Code: skill-creator if present, otherwise the full skill written in chat | n/a | n/a | | |
| 6.6 | Never says the skill is saved before you saved it | | | | |
| 6.7 | "No": accepted in one line, nothing drafted, label last | | | | |
| 6.8 | "How do I get better at delegation?": help-me-improve, no level, no score, no label, reads no chat | | | | |

## 7. Export

| # | Check | Chat | Cowork | CC | Notes |
|---|---|---|---|---|---|
| 7.1 | "Export this": plan with up to 5 quotes tied to scored capabilities, title, date; "Nothing has been written." | | | | |
| 7.2 | Drop a quote by number: it appears nowhere in the report | | | | |
| 7.3 | "Scores only": empty evidence, no quote anywhere | | | | |
| 7.4 | Report: title, date, label, table, note on not-shown "low", evidence, record block last | | | | |
| 7.5 | No summary, next-level notes, improvements or Claude text in the report | | | | |
| 7.6 | Where files can be created: offers `modo-assessment-<date>.md`, writes only after "save it", says the path | | | | |
| 7.7 | Where files can't be created: says so, no claim of a file | | | | |
| 7.8 | "As a PDF": PDF made only on request and only where file creation exists; otherwise says so before the report | | | | |
| 7.9 | Record validates: save the report (or the block) and run `python3 scripts/validate_assessment_record.py <file>` (and once with `--spec-only`) | | | | |
| 7.10 | "Upload it to Modo": says you upload it yourself; doesn't upload or offer to | | | | |
| 7.11 | Export with no assessment, or after a too-short message: "nothing to export yet", no report | | | | |

## 8. Sign-off

| Item | Result | Notes |
|---|---|---|
| Any run that read, listed or searched another chat or file | | |
| Any run without the exact label | | |
| README claims that didn't match what you saw | | |
| Tester, date, app versions | | |
