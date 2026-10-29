"""Fill the passport card template with a result (used by tests and for the
sample screenshot). The skill does the same replacement itself: it swaps the
JSON between the two markers and leaves everything else untouched.

    python3 scripts/fill_passport_card.py OUT.html   # fills the sample
"""
import json
import pathlib
import re
import sys

TEMPLATE = (pathlib.Path(__file__).resolve().parent.parent / "plugins" / "modo-ai-skills"
            / "skills" / "assess-my-ai-work" / "passport-card.html")

# Synthetic illustration for the card's sample images, not a scored result:
# the levels are chosen to show every state (strong, medium, low confidence,
# not shown); the scored version of this chat is ASSESSMENT_STRONG in
# scripts/gen_ai_skills_eval_history.py. Quotes are verbatim user messages
# from the strong-verify-weak-delegate chat's history.jsonl.
SAMPLE = {
    "chat": "this chat",
    "sessions": 1,
    "capabilities": [
        {"name": "Problem Solving", "level": 4, "confidence": "medium", "agreement": "3 of 3 runs"},
        {"name": "Verification", "level": 5, "confidence": "high", "agreement": "3 of 3 runs"},
        {"name": "Workflow Design", "level": 2, "confidence": "low", "agreement": "2 of 3 runs"},
        {"name": "Delegation", "level": 2, "confidence": "medium", "agreement": "3 of 3 runs"},
        {"name": "Strategic Thinking", "level": "not_shown", "agreement": "3 of 3 runs"},
    ],
    "evidence": [
        {"capability": "Verification",
         "quote": "You also said enterprise tiers typically grow 20-25% quarter on quarter. What is that based on? Give me a source I can open, or tell me it's a guess so I can cut it."},
        {"capability": "Problem Solving",
         "quote": "Rerun it three ways: no change in churn, 5% extra churn, 10% extra churn."},
    ],
    "growth": {"capability": "Delegation",
               "tip": "When you hand over the deck, say what each slide must contain and ask to see the outline before Claude writes the rest."},
    "next_action": "Assess one more chat with different work to see Strategic Thinking.",
}

START = "<!-- MODO-DATA-START -->"
END = "<!-- MODO-DATA-END -->"


def fill(template: str, data: dict) -> str:
    """Replace the data block between the markers. `<` is escaped so a quote
    can never close the script element."""
    block = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    new = (f'{START}\n<script type="application/json" id="passport-data">\n'
           f"{block}\n</script>\n{END}")
    out, n = re.subn(re.escape(START) + ".*?" + re.escape(END),
                     lambda _: new, template, flags=re.S)
    if n != 1:
        raise ValueError("data markers not found exactly once")
    return out


if __name__ == "__main__":
    pathlib.Path(sys.argv[1]).write_text(fill(TEMPLATE.read_text(), SAMPLE))
