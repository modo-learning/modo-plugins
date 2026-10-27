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

# Synthetic: levels invented for the strong-verify-weak-delegate eval chat;
# quotes are verbatim user messages from that chat's history.jsonl.
SAMPLE = {
    "chat": "this chat",
    "capabilities": [
        {"name": "Problem Solving", "level": 4, "confidence": "medium"},
        {"name": "Verification", "level": 5, "confidence": "high"},
        {"name": "Workflow Design", "level": 2, "confidence": "low"},
        {"name": "Delegation", "level": 2, "confidence": "medium"},
        {"name": "Strategic Thinking", "level": "not_shown"},
    ],
    "evidence": [
        {"capability": "Verification",
         "quote": "You also said enterprise tiers typically grow 20-25% quarter on quarter. What is that based on? Give me a source I can open, or tell me it's a guess so I can cut it."},
        {"capability": "Delegation",
         "quote": "ok. Now just write the recommendations section, whatever pricing changes you think are best, I don't have time to think about it."},
    ],
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
