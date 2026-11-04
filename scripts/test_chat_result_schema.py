"""python3 -m unittest scripts/test_chat_result_schema.py

skills/assess-my-chats/chat-result.schema.json is the JSON Schema of a
ChatResult (what each chat agent returns). validate_chat_result.py stays
authoritative for the rules a schema can't hold (too_short against
user_messages, runs against agreement, quotes against the chat). These tests
check that the brief points at the schema, that the schema's fields are the
validator's, and that the brief's examples and every fixture's expected.json
satisfy both.

No jsonschema dependency: when the package is missing, a small checker below
handles the keywords the schema uses (and fails on any other keyword).
"""

import copy
import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from test_chat_agent_brief import BRIEF, json_blocks  # noqa: E402
from validate_chat_result import (CAP_FIELDS, CAPABILITIES, CONFIDENCE, MAX_QUOTE, RUN_KINDS, TASK_TYPES,  # noqa: E402
                                  TOP, validate)

SCHEMA_PATH = BRIEF.parent / "chat-result.schema.json"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
KNOWN = {"$schema", "$id", "title", "description", "$defs", "$ref", "type", "const", "enum", "required",
         "properties", "additionalProperties", "items", "minItems", "maxItems", "minLength", "maxLength",
         "minimum", "maximum", "pattern", "oneOf"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def schema():
    return json.loads(SCHEMA_PATH.read_text())


def _type_ok(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, TYPES[t])


def check(value, node, root, where="$"):
    """Errors for `value` against schema `node` (the keywords in KNOWN only)."""
    unknown = set(node) - KNOWN
    if unknown:
        return [f"{where}: schema keyword(s) {sorted(unknown)} not handled by this checker"]
    if "$ref" in node:
        return check(value, root["$defs"][node["$ref"].split("/")[-1]], root, where)
    if "oneOf" in node:
        passing = [s for s in node["oneOf"] if not check(value, s, root, where)]
        return [] if len(passing) == 1 else [f"{where}: matches {len(passing)} of oneOf, not 1"]
    errors = []
    if "type" in node:
        types = node["type"] if isinstance(node["type"], list) else [node["type"]]
        if not any(_type_ok(value, t) for t in types):
            return [f"{where}: not {types}"]
    if "const" in node and value != node["const"]:
        errors.append(f"{where}: not {node['const']!r}")
    if "enum" in node and value not in node["enum"]:
        errors.append(f"{where}: not one of {node['enum']}")
    if isinstance(value, str):
        if len(value) < node.get("minLength", 0) or len(value) > node.get("maxLength", float("inf")):
            errors.append(f"{where}: length {len(value)}")
        if "pattern" in node and not re.search(node["pattern"], value):
            errors.append(f"{where}: does not match {node['pattern']}")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < node.get("minimum", float("-inf")) or value > node.get("maximum", float("inf")):
            errors.append(f"{where}: {value} out of range")
    if isinstance(value, list):
        if len(value) < node.get("minItems", 0) or len(value) > node.get("maxItems", float("inf")):
            errors.append(f"{where}: {len(value)} items")
        for i, item in enumerate(value):
            errors += check(item, node.get("items", {}), root, f"{where}[{i}]")
    if isinstance(value, dict):
        errors += [f"{where}: missing {k}" for k in node.get("required", []) if k not in value]
        props = node.get("properties", {})
        if node.get("additionalProperties") is False:
            errors += [f"{where}: unknown {k}" for k in value if k not in props]
        for k, sub in props.items():
            if k in value:
                errors += check(value[k], sub, root, f"{where}.{k}")
    return errors


def schema_errors(value):
    s = schema()
    try:
        import jsonschema  # optional
    except ImportError:
        return check(value, s, s)
    return [e.message for e in jsonschema.Draft202012Validator(s).iter_errors(value)]


def examples():
    """(name, ChatResult): the brief's examples and every fixture's expected.json."""
    out = [(f"brief:{b['chat_id']}", b) for b in json_blocks(BRIEF.read_text())]
    out += [(str(p.relative_to(FIXTURES)), json.loads(p.read_text()))
            for p in sorted(FIXTURES.glob("*/*/expected.json"))]
    return out


class Schema(unittest.TestCase):
    def test_brief_points_at_the_schema(self):
        self.assertIn("[chat-result.schema.json](chat-result.schema.json)", BRIEF.read_text())
        self.assertTrue(SCHEMA_PATH.is_file())

    def test_examples_satisfy_the_schema_and_the_validator(self):
        found = examples()
        self.assertGreaterEqual(len(found), 7)
        for name, result in found:
            with self.subTest(example=name):
                self.assertEqual(schema_errors(result), [])
                self.assertEqual(validate(result), [])

    def test_field_names_agree_with_the_validator(self):
        s = schema()
        self.assertEqual(set(s["required"]), TOP)
        self.assertEqual(set(s["properties"]), TOP)
        self.assertFalse(s["additionalProperties"])
        caps = s["properties"]["capabilities"]
        self.assertEqual(list(caps["properties"]), list(CAPABILITIES))
        self.assertEqual(caps["required"], list(CAPABILITIES))
        cap = s["$defs"]["capability"]
        self.assertEqual(set(cap["required"]), CAP_FIELDS)
        self.assertEqual(set(cap["properties"]), CAP_FIELDS)
        self.assertEqual(tuple(cap["properties"]["confidence"]["enum"]), CONFIDENCE)
        self.assertEqual(tuple(s["properties"]["run_kind"]["enum"]), RUN_KINDS)
        self.assertEqual(s["$defs"]["quote"]["properties"]["text"]["maxLength"], MAX_QUOTE)
        self.assertEqual(tuple(s["properties"]["task_type"]["enum"]), TASK_TYPES + (None,))

    def test_the_schema_rejects_what_the_validator_rejects(self):
        good = examples()[0][1]
        bad = [("extra field", lambda r: r.update(transcript="...")),
               ("level 6", lambda r: r["capabilities"]["verification"].update(level=6)),
               ("level 4.0", lambda r: r["capabilities"]["verification"].update(level="4")),
               ("unknown capability", lambda r: r["capabilities"].update(prompting={})),
               ("long quote", lambda r: r["capabilities"]["verification"]["quotes"][0].update(text="x" * 241)),
               ("bad behaviour id", lambda r: r["capabilities"]["verification"].update(behaviours=["X9"])),
               ("runs 4", lambda r: r.update(runs=4)),
               ("task type Other", lambda r: r.update(task_type="Other")),
               ("agent session as a bare yes", lambda r: r.update(agent_session=True)),
               ("reuse without its quote field", lambda r: r.update(reuse={"value": False})),
               ("bad agreement", lambda r: r["capabilities"]["verification"].update(agreement="most runs"))]
        for name, change in bad:
            with self.subTest(change=name):
                r = copy.deepcopy(good)
                change(r)
                self.assertTrue(schema_errors(r))
                self.assertTrue(validate(r))


if __name__ == "__main__":
    unittest.main()
