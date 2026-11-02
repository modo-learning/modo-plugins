"""python3 -m unittest scripts/test_build_openai_plugin.py"""

import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_openai_plugin as build  # noqa: E402

OUT = build.OUT
SKILL_TEXT = [p for p in OUT.rglob("*") if p.is_file() and build.LABEL_FILES.match(p.name)]
# Claude-only wording that must not reach the OpenAI build.
CLAUDE_ONLY = re.compile(r"claude\.ai|Cowork|Claude Code|Claude's|to Claude|by Claude|artifact tool|"
                         r"save_assessment|save-to-passport|Modo connector is present|/assess-my-ai-work|"
                         r"/help-me-improve|/export-assessment")
# The one sanctioned mention: the note that maps the shared files' "Claude" to the assistant.
NOTE = re.compile(r'first written for Claude|says "Claude"|^"Claude", read')


class CommittedBuild(unittest.TestCase):
    def test_committed_output_is_up_to_date(self):
        self.assertEqual(build.check(), [])

    def test_only_the_v1_skills_ship(self):
        shipped = sorted(p.name for p in (OUT / "skills").iterdir())
        self.assertEqual(shipped, sorted(build.SKILLS))
        self.assertFalse((OUT / "mcp.json").exists())
        self.assertFalse((OUT / ".claude-plugin").exists())

    def test_shared_files_are_byte_identical_to_the_claude_plugin(self):
        shared = [p for p in OUT.rglob("*") if build.SHARED_AS_IS.match(p.name)]
        self.assertGreaterEqual(len(shared), 4)
        for path in shared:
            with self.subTest(path=path.name):
                source = build.SOURCE / path.relative_to(OUT)
                self.assertEqual(path.read_bytes(), source.read_bytes())

    def test_no_claude_only_wording_in_skill_text_or_templates(self):
        for path in SKILL_TEXT:
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if NOTE.search(line):
                    continue
                with self.subTest(file=str(path.relative_to(OUT)), line=n):
                    self.assertIsNone(CLAUDE_ONLY.search(line), line)
                    self.assertNotIn("Claude", line)

    def test_the_level_script_ships_unchanged_and_the_skill_uses_it(self):
        for rel, source in build.EXTRA.items():
            self.assertEqual((OUT / rel).read_bytes(), source.read_bytes())
        skill = (OUT / "skills" / "assess-my-ai-work" / "SKILL.md").read_text()
        self.assertIn("scripts/derive_levels.py", skill)
        self.assertIn("needs_more_runs", skill)

    def test_every_label_names_chatgpt(self):
        labels = [line for p in SKILL_TEXT for line in p.read_text().splitlines() if "Self-assessment by" in line]
        self.assertGreaterEqual(len(labels), 4)
        for line in labels:
            self.assertIn(build.LABEL_TO, line)

    def test_every_skill_has_name_and_description(self):
        for skill in build.SKILLS:
            with self.subTest(skill=skill):
                head = (OUT / "skills" / skill / "SKILL.md").read_text().split("---")[1]
                self.assertRegex(head, rf"(?m)^name: {re.escape(skill)}$")
                self.assertRegex(head, r"(?m)^description: \S")

    def test_manifest_matches_the_claude_plugin_and_the_schema(self):
        data = json.loads((OUT / "plugin.json").read_text())
        claude = json.loads((build.SOURCE / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(build.validate_manifest(data), [])
        for key in ("name", "version", "license", "author"):
            self.assertEqual(data[key], claude[key])
        self.assertEqual(data["extensions"]["com.openai"]["interface"]["displayName"], "Modo AI Skills")

    def test_marketplace_points_at_the_build(self):
        market = json.loads(build.MARKETPLACE.read_text())
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], "modo-ai-skills")
        self.assertEqual((build.ROOT / entry["source"]["path"]).resolve(), OUT.resolve())


class Patches(unittest.TestCase):
    def test_a_find_must_match_exactly_once(self):
        with self.assertRaisesRegex(build.BuildError, "found 0 times"):
            build.apply_patch("abc", [("xyz", "q")], "f")
        with self.assertRaisesRegex(build.BuildError, "found 2 times"):
            build.apply_patch("ab ab", [("ab", "q")], "f")
        self.assertEqual(build.apply_patch("one two", [("two", "2")], "f"), "one 2")

    def test_parse_reads_multi_line_blocks_and_empty_replacements(self):
        text = "header\n\n<<<<<<< FIND\na\nb\n=======\nc\n>>>>>>> REPLACE\n\n<<<<<<< FIND\nd\n=======\n>>>>>>> REPLACE\n"
        self.assertEqual(build.parse_patch(text), [("a\nb", "c"), ("d", "")])

    def test_a_patch_with_no_blocks_fails(self):
        with self.assertRaises(build.BuildError):
            build.parse_patch("just text")

    def test_every_patch_block_applies_to_the_current_source(self):
        for patch in build.OVERLAYS.rglob("*.patch"):
            rel = patch.relative_to(build.OVERLAYS)
            with self.subTest(patch=str(rel)):
                source = (build.SOURCE / "skills" / rel.parent / rel.stem).read_text()
                build.apply_patch(source, build.parse_patch(patch.read_text()), str(rel))


class Manifest(unittest.TestCase):
    def test_validator_rejects_unknown_fields_and_bad_names(self):
        self.assertIn("unknown field displayName", build.validate_manifest(
            {"$schema": build.SCHEMA_URL, "name": "ok", "displayName": "x"}))
        self.assertIn("name does not match the schema pattern", build.validate_manifest(
            {"$schema": build.SCHEMA_URL, "name": "Bad Name"}))
        self.assertIn("missing name", build.validate_manifest({"$schema": build.SCHEMA_URL}))


if __name__ == "__main__":
    unittest.main()
