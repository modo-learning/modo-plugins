"""python3 -m unittest scripts/test_rubric_common.py

The constants and small checks that the record validator, the ChatResult
validator and the aggregation share have one source, rubric_common.py.
"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import aggregate_chats  # noqa: E402
import derive_levels  # noqa: E402
import rubric_common as common  # noqa: E402
import validate_assessment_record as record  # noqa: E402
import validate_chat_result as chat_result  # noqa: E402


class OneSource(unittest.TestCase):
    def test_validators_and_aggregation_use_the_shared_constants(self):
        for module in (record, chat_result, aggregate_chats):
            with self.subTest(module=module.__name__):
                self.assertIs(module.CAPABILITIES, common.CAPABILITIES)
        for module in (record, chat_result):
            with self.subTest(module=module.__name__):
                self.assertIs(module.CONFIDENCE, common.CONFIDENCE)
                self.assertIs(module.MAX_QUOTE, common.MAX_QUOTE)

    def test_capabilities_in_rubric_order(self):
        self.assertEqual(common.CAPABILITIES, ("problem_solving", "verification", "workflow_design",
                                               "delegation", "strategic_thinking"))

    def test_the_json_not_shown_value_is_not_derive_levels_display_text(self):
        # derive_levels.py is copied on its own into the ChatGPT version, so it
        # keeps its own constants; its NOT_SHOWN is display text with a space.
        self.assertEqual(common.LEVEL_NOT_SHOWN, "not_shown")
        self.assertEqual(derive_levels.NOT_SHOWN, "not shown")
        self.assertEqual(derive_levels.CONFIDENCE, common.CONFIDENCE)


class Checks(unittest.TestCase):
    def test_is_int(self):
        self.assertTrue(common.is_int(0))
        self.assertFalse(common.is_int(True))
        self.assertFalse(common.is_int(4.0))
        self.assertFalse(common.is_int(-1, low=0))
        self.assertTrue(common.is_int(-1))

    def test_is_level(self):
        self.assertEqual([common.is_level(v) for v in (1, 5, "not_shown", 0, 6, "not shown", True, 3.0)],
                         [True, True, True, False, False, False, False, False])

    def test_date_is_a_whole_real_date(self):
        self.assertTrue(common.is_date("2026-10-30"))
        self.assertFalse(common.is_date("2026-10-30T10:00:00Z"))
        self.assertFalse(common.is_date("2026-02-30"))
        self.assertIsNone(common.DATE.match("2026-10-30T10:00:00Z"))


if __name__ == "__main__":
    unittest.main()
