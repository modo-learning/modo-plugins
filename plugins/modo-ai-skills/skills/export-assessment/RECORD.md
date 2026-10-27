# Modo AI Skills assessment record

**Record version: matches rubric v1**

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

| Field | Type | Rule |
|---|---|---|
| `rubric_version` | string | `v` followed by digits, such as `v1`. Must be a rubric version the receiver knows. |
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
  "rubric_version": "v1",
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

Stdlib only. It enforces every limit in the table. Without `--spec-only` it
also enforces conventions 1 and 2. Unit tests:
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
