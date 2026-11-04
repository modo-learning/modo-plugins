"""Constants and small checks shared by the validators and the aggregation (stdlib only).

validate_assessment_record.py, validate_chat_result.py and aggregate_chats.py
import these; edit them here only. derive_levels.py keeps its own copies on
purpose: it is copied on its own into the ChatGPT version, so it imports
nothing from this folder (test_rubric_common.py checks its CONFIDENCE matches).
"""

import datetime
import re

# The five capability keys, in rubric order.
CAPABILITIES = ("problem_solving", "verification", "workflow_design", "delegation", "strategic_thinking")
CONFIDENCE = ("low", "medium", "high")
MAX_QUOTE = 240
# Johnny's scoring rules v1, section 3. A chat gets exactly one, the closest match.
TASK_TYPES = ("Writing and editing", "Research and summarizing", "Data analysis", "Coding",
              "Planning and decisions", "Brainstorming", "Learning", "Operations and admin")
# The JSON value for a capability with no level. Not derive_levels.NOT_SHOWN,
# which is the display text "not shown" (with a space).
LEVEL_NOT_SHOWN = "not_shown"
# A whole date, yyyy-mm-dd and nothing else. For a timestamp, match its first 10 characters.
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_int(v, low=None):
    """A JSON integer (not a bool, not 4.0), at least `low` when given."""
    return isinstance(v, int) and not isinstance(v, bool) and (low is None or v >= low)


def is_level(v):
    """A capability level: an integer 1 to 5 or "not_shown"."""
    return v == LEVEL_NOT_SHOWN or (is_int(v) and 1 <= v <= 5)


def is_date(d):
    """A real calendar date written yyyy-mm-dd."""
    if not (isinstance(d, str) and DATE.match(d)):
        return False
    try:
        datetime.date.fromisoformat(d)
        return True
    except ValueError:
        return False
