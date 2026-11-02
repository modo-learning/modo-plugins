# Modo AI Skills assessment record

**Record version: matches rubric v1.1**

The record is the only data that may leave Claude when a user exports an
assessment or saves it to their Modo passport (it is the whole input of the
Modo connector's `save_assessment` tool). It holds
scores, confidence, a few quotes the user approved, a title and a date. It
never holds the chat, Claude's replies, the next-level notes or the
improvements.

Source: the "Assessment record" section of SPEC-modo-ai-skills.md. Where this
file adds something the spec does not say, it is listed under
[Decisions that go beyond the spec](#decisions-that-go-beyond-the-spec).

## Fields

No other fields are allowed, at any level. A record with an unknown field is
invalid.

There are two shapes. A record **without** a `scope` field is a single-chat
record: the table below, unchanged. A record with `scope: "multi_chat"` is the
result of several chats combined (the assess-my-chats skill); it adds fields,
listed under [Multi-chat record](#multi-chat-record-proposal). No other `scope`
value exists.

| Field | Type | Rule |
|---|---|---|
| `rubric_version` | string | `v` followed by digits, with an optional `.` and more digits, such as `v1` or `v1.1`. Must be a rubric version the receiver knows. |
| `capabilities` | object | Exactly the five keys below, each present. |
| `capabilities.<key>.level` | integer or string | An integer 1 to 5 written without a decimal point (`4`, never `4.0`), or the string `"not_shown"`. |
| `capabilities.<key>.confidence` | string | `"low"`, `"medium"` or `"high"`. Always present, also for `not_shown`. |
| `evidence` | array | At most 5 items. Empty (`[]`) for a scores-only export or save. |
| `evidence[].capability` | string | One of the five keys. |
| `evidence[].quote` | string | 1 to 240 characters (Unicode characters, not bytes). A word-for-word excerpt of a message the user wrote, which the user approved. |
| `session_title` | string | 1 to 120 characters. |
| `session_date` | string | A real calendar date as `yyyy-mm-dd` (ISO 8601), the day of the assessed chat. |

The five capability keys, in rubric order: `problem_solving`, `verification`,
`workflow_design`, `delegation`, `strategic_thinking`.

## Example

```json
{
  "rubric_version": "v1.1",
  "capabilities": {
    "problem_solving": { "level": 4, "confidence": "medium" },
    "verification": { "level": 4, "confidence": "high" },
    "workflow_design": { "level": 2, "confidence": "medium" },
    "delegation": { "level": 1, "confidence": "medium" },
    "strategic_thinking": { "level": "not_shown", "confidence": "low" }
  },
  "evidence": [
    {
      "capability": "verification",
      "quote": "Team is 310 against 280, which is 10.7%, not 14.3%."
    }
  ],
  "session_title": "Q3 pricing analysis for the board",
  "session_date": "2026-10-20"
}
```

A JSON Schema for the same rules is in
[assessment-record.schema.json](assessment-record.schema.json) (draft 2020-12).
It cannot express everything, so **the validator
(`scripts/validate_assessment_record.py` in the modo-plugins repo) is
authoritative** where they differ:

- The two conventions below are not in the schema.
- A level written as `4.0`: JSON Schema's `integer` type accepts any number
  with a zero fraction, so the schema lets `4.0` through; the validator
  rejects it. A receiver (the Modo platform) must likewise reject a level
  that is a non-integer JSON number token, for example by checking the parsed
  value's type rather than relying on a schema validator alone.

## Multi-chat record (proposal)

**Proposal, decided 2026-11-02, flag for review** (card look: Angelina;
server acceptance: Keith). The Modo connector
does not accept this shape yet: save works only once modo-mcp accepts it.

A multi-chat record has every single-chat field, with these changes, and the
fields below. `rubric_version` stays `"v1.1"`.

| Field | Type | Rule |
|---|---|---|
| `scope` | string | Exactly `"multi_chat"`. Absent means a single chat. |
| `capabilities.<key>` | object | Exactly `level`, `confidence`, `best_shown`, `trend`, `chats_shown`. |
| `capabilities.<key>.level` | integer or string | The combined level: the lower median of the per-chat levels where it was shown, or `"not_shown"`. |
| `capabilities.<key>.confidence` | string | The combined confidence by the aggregation rules (`"low"` when not shown). |
| `capabilities.<key>.best_shown` | integer or null | The highest level reached in at least 2 chats; `null` if none. |
| `capabilities.<key>.trend` | string or null | `"up"`, `"flat"` or `"down"` when shown in 4 or more chats, else `null`. |
| `capabilities.<key>.chats_shown` | integer | In how many scored chats it was shown. |
| `evidence[]` | object | Exactly `capability`, `chat`, `quote`. |
| `evidence[].chat` | integer | The number of the chat in `chats` (1 is the first) that the quote comes from. That chat is scored and shows the capability. |
| `session_title` | string | 1 to 120 characters. Default "Assessment across N chats" (N scored chats); no chat title in it unless the user approved it. |
| `session_date` | string | The date of the newest scored chat (equals `chats_assessed.to`). |
| `chats_assessed` | object | Exactly `count`, `scored`, `too_short`, `could_not_be_read`, `from`, `to`. |
| `chats_assessed.count` | integer | The number of entries in `chats`, 1 to 25. |
| `chats_assessed.scored`, `.too_short`, `.could_not_be_read` | integer | How many entries in `chats` have each result. They add up to `count`. At least one chat is scored. |
| `chats_assessed.from`, `.to` | string | The oldest and newest scored chat's date, `yyyy-mm-dd`. |
| `chats` | array | 1 to 25 per-chat summaries, newest first, the order the user confirmed. |
| `chats[].title` | string | 1 to 120 characters. `"Chat 1"`, `"Chat 2"`, … by position, unless the user approved including the chat titles. |
| `chats[].date` | string | The chat's date as the chat list gave it, `yyyy-mm-dd`. |
| `chats[].result` | string | `"scored"`, `"too_short"` or `"could_not_be_read"`. |
| `chats[].levels` | object or null | For a scored chat, the five capability keys, each an integer 1 to 5 or `"not_shown"`. `null` for a chat that was not scored. |
| `coverage` | integer | How many of the five capabilities were shown in at least one scored chat (0 to 5). |

Rules that tie the record together (the validator checks each one):

- The combined `level`, `confidence`, `best_shown`, `trend` and `chats_shown`
  of every capability are exactly what the aggregation rules below give for
  the per-chat levels in `chats`.
- `coverage` is the number of capabilities whose combined level is not
  `"not_shown"`.
- The counts in `chats_assessed` match `chats`; `from`, `to` and
  `session_date` match the scored chats' dates.
- A per-chat summary holds no quotes, no message counts and nothing else from
  the chat. Quotes are only in `evidence`, after the user approved them.

The aggregation rules (the same as assess-my-chats, step 4), per capability,
over the scored chats where it was shown (level 1 to 5):

- `level`: the median of their levels; with an even number, the lower of the
  two middle ones.
- `best_shown`: the highest level reached in at least 2 chats; `null` if no
  level was reached twice.
- `confidence`: high when shown in 3 or more chats with a spread (highest
  minus lowest) of at most 1; medium when shown in 2 chats with a spread of
  at most 1, or in 3 or more chats with a spread of 2; low otherwise.
- `trend`: only when shown in 4 or more chats, else `null`. Order those chats
  by date, oldest first (two chats with the same date: the one later in
  `chats` counts as older). Take the median (lower middle) of the earlier half
  and of the later half; with an odd number, leave out the middle chat.
  `"up"` if the later is higher, `"down"` if lower, else `"flat"`.
- `chats_shown`: how many scored chats show it.
- Shown in no scored chat: `"not_shown"`, confidence `"low"`, `best_shown`
  and `trend` `null`, `chats_shown` 0.

### Multi-chat example

```json
{
  "rubric_version": "v1.1",
  "scope": "multi_chat",
  "capabilities": {
    "problem_solving": { "level": 2, "confidence": "high", "best_shown": 3, "trend": "up", "chats_shown": 4 },
    "verification": { "level": 3, "confidence": "high", "best_shown": 4, "trend": "up", "chats_shown": 4 },
    "workflow_design": { "level": 2, "confidence": "medium", "best_shown": 2, "trend": null, "chats_shown": 3 },
    "delegation": { "level": 3, "confidence": "medium", "best_shown": null, "trend": null, "chats_shown": 3 },
    "strategic_thinking": { "level": "not_shown", "confidence": "low", "best_shown": null, "trend": null, "chats_shown": 0 }
  },
  "evidence": [
    {
      "capability": "verification",
      "chat": 4,
      "quote": "Before we use that number, show me the query you ran so I can rerun it."
    }
  ],
  "session_title": "Assessment across 4 chats",
  "session_date": "2026-10-30",
  "chats_assessed": { "count": 5, "scored": 4, "too_short": 1, "could_not_be_read": 0, "from": "2026-10-06", "to": "2026-10-30" },
  "chats": [
    { "title": "Chat 1", "date": "2026-10-30", "result": "scored",
      "levels": { "problem_solving": 3, "verification": 4, "workflow_design": 2, "delegation": "not_shown", "strategic_thinking": "not_shown" } },
    { "title": "Chat 2", "date": "2026-10-27", "result": "scored",
      "levels": { "problem_solving": 3, "verification": 4, "workflow_design": 4, "delegation": 4, "strategic_thinking": "not_shown" } },
    { "title": "Chat 3", "date": "2026-10-21", "result": "too_short", "levels": null },
    { "title": "Chat 4", "date": "2026-10-14", "result": "scored",
      "levels": { "problem_solving": 2, "verification": 3, "workflow_design": 2, "delegation": 3, "strategic_thinking": "not_shown" } },
    { "title": "Chat 5", "date": "2026-10-06", "result": "scored",
      "levels": { "problem_solving": 2, "verification": 3, "workflow_design": "not_shown", "delegation": 2, "strategic_thinking": "not_shown" } }
  ],
  "coverage": 4
}
```

Invalid examples, each with the error the validator gives, are in
`scripts/fixtures/records/` in the modo-plugins repo.

### Multi-chat decisions (decided 2026-11-02, flag for review)

- **M1.** **Absent `scope` means a single chat.** Single-chat records stay valid and
  unchanged, so nothing already saved or exported changes. `"single_chat"`
  is not a value: one way to say one thing.
- **M2.** **The combined fields are checked, not trusted.** The per-chat levels are
  in the record, so the validator recomputes every combined value. A record
  whose combined levels don't follow from its own chats is invalid.
- **M3.** **Chat titles are user content.** Like quotes, they go in only if the user
  approves (at export or save); otherwise `"Chat 1"` … `"Chat N"`. The
  default `session_title` names no chat.
- **M4.** **Dates are days, not times.** `chats[].date` is `yyyy-mm-dd`, the same
  precision as `session_date`; the trend uses the order of `chats` (newest
  first, as the chat list gave them), so same-day chats keep their order.
- **M5.** **`session_date` is the newest scored chat's date**, so a passport that
  orders by `session_date` places a multi-chat record by its latest chat.
- **M6.** **A quote names its chat by number** (`evidence[].chat`), not by title,
  so a quote can be tied to a chat without its title. Convention (like 1
  and 2 below): the chat's level for that capability equals the combined level,
  the same rule the assess-my-chats answer uses to pick evidence.
- **M7.** **No per-chat confidence, runs or message counts.** The card and report
  need only the levels; less data leaves Claude. Not specified by the
  design: whether Modo wants them.

## Decisions that go beyond the spec

These are plugin choices, made as standard practice. They can change with
Angelina's review.

1. **`confidence` for `not_shown` is `"low"`.** The spec asks for a confidence
   on every capability, and the rubric defines confidence only for a scored
   level (it counts moments that support a level; `not_shown` has none, so no
   rubric definition applies). `"low"` is the honest value: no moment supports a
   level. The report says so in a footnote. The alternative, leaving
   confidence out, breaks the "exactly these fields" rule.
2. **No quote for a `not_shown` capability.** The rubric says a quote must bear
   on its capability, and `not_shown` means nothing did.
3. **Capabilities are an object keyed by id, not a list.** This makes "exactly
   five, each once" a property of the shape. Spec wording ("each with `level`
   and `confidence`") does not fix list or object. `save_assessment` takes
   exactly this record as its arguments (modo-mcp README). Not specified: what
   the upload page expects.
4. **Quote tied to a capability by key.** The spec says "tied to a capability"
   without a field name; `capability` is the plugin's choice.

## How a parser finds the record in a report

The Markdown report ends with the record in a fenced block whose language tag
is `json`, under the heading "Assessment record (machine-readable)":

- The record is the **last** `json` fenced block in the file.
- Nothing follows it except whitespace. When the report is shown in chat
  instead of saved, the result label line may follow, and nothing else.
- The report has no other `json` block.

## Checking a record

The validator is `scripts/validate_assessment_record.py` in the modo-plugins
repo (it does not ship with the plugin). From the repo root:

```
python3 scripts/validate_assessment_record.py report.md     # last json block
python3 scripts/validate_assessment_record.py record.json   # bare JSON
python3 scripts/validate_assessment_record.py report.md --spec-only
```

Stdlib only. It enforces every limit in the tables and every multi-chat rule
above. Without `--spec-only` it also enforces conventions 1, 2 and M6. Unit tests:
`python3 -m unittest scripts/test_validate_assessment_record.py`.

Whether each quote is really a word-for-word excerpt of the user's messages
cannot be checked from the record alone; the skill that proposes the record
(export or save) checks it against the chat before proposing it, and the
receiver cannot check it without the chat.

## Checking the records in an eval run

Eval graders only read the final message and cannot run Python. After a run,
check the saved result instead (scripts in the modo-plugins repo, run from
its root). The eval runner writes
`aggregate-result.json` under `evals/results/<timestamp>/` (that file name and
its layout were checked against this plugin's earlier runs; the layout of
other CLI versions is not specified):

```
python3 scripts/check_eval_records.py plugins/modo-ai-skills/evals/results/<timestamp>/aggregate-result.json
```

It reads the final message of every run of the `export-*` cases from the
LLM-grader `evidence` fields, extracts the record and validates it with the
script above. `export-scores-only` must also have an empty `evidence` list.
For the `save-*` cases that send a record it reads the calls to the mocked
`save_assessment` tool (from an LLM grader with `focus: mock_calls`), requires
exactly one call per run and validates its input the same way, including the
number of quotes the case expects, and requires it to equal the record the
case's history showed.
Tests: `python3 -m unittest scripts/test_check_eval_records.py`.

**Run the save cases with `scripts/run_save_evals.py`, not with
`claude plugin eval` alone.** A mocked tool's `expect:` guards cannot reject an
unknown field (a transcript) or more than 5 quotes, and LLM graders only judge;
so an eval run can pass with a record this check rejects. The script runs
`claude plugin eval` for each save case and then this check on its result, and
exits non-zero if either fails:

```
python3 scripts/run_save_evals.py                        # every save case
python3 scripts/run_save_evals.py --runs 2 save-confirmed save-declined
```

## Open question for Angelina

What does the Modo platform upload page accept: the `.md` report, the bare
JSON, a PDF, or only one of them? Until that is answered, the export produces
the Markdown report (with the record last) and a PDF only on request, and the
user uploads it themselves. The export never uploads anything; the only
thing this plugin sends anywhere is this record, through the Modo connector's
`save_assessment` tool, after the user has seen it and said yes.

## Copies

This file and the schema exist twice, because skill docs only cover files
bundled in the skill's own folder: in `skills/export-assessment/` (the source:
edit there) and in `skills/save-to-passport/`. Both skills build the record
by these rules: export-assessment writes it into a report, save-to-passport
sends it to the Modo passport. Copy both files over after every edit.
`scripts/check_rubric_sync.py` (modo-plugins repo) fails when the copies
differ, the same way it compares the rubric copies. The schema's `$id` names
the export copy as the canonical one in both folders: the copies are
identical, so one identifier serves both.
