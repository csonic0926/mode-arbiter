from __future__ import annotations

import importlib.util
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_PATH = ROOT / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("mode_arbiter_install", INSTALL_PATH)
assert SPEC is not None and SPEC.loader is not None
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


class SetRootModelInstructionsTests(unittest.TestCase):
    def assert_updated(self, source: str) -> dict:
        updated = INSTALL.set_root_model_instructions(source)
        self.assertEqual(INSTALL.set_root_model_instructions(updated), updated)
        parsed = tomllib.loads(updated)
        self.assertEqual(
            parsed["model_instructions_file"], INSTALL.MODEL_INSTRUCTIONS_VALUE
        )
        return parsed

    def test_inserts_key_before_tables(self) -> None:
        parsed = self.assert_updated(
            'model = "gpt"\n\n[features]\njs_repl = false\n'
        )
        self.assertFalse(parsed["features"]["js_repl"])
        self.assertNotIn("model_instructions_file", parsed["features"])

    def test_replaces_single_quoted_root_key_with_inline_comment(self) -> None:
        parsed = self.assert_updated(
            "model_instructions_file = '/old.md' # stale\nmodel = 'gpt'\n"
        )
        self.assertEqual(parsed["model"], "gpt")

    def test_does_not_mistake_nested_key_for_root_key(self) -> None:
        parsed = self.assert_updated(
            '[features]\nmodel_instructions_file = "/nested.md"\n'
        )
        self.assertEqual(parsed["features"]["model_instructions_file"], "/nested.md")

    def test_collapses_duplicate_root_keys(self) -> None:
        parsed = self.assert_updated(
            'model_instructions_file = "/a"\n'
            'model_instructions_file = "/b"\n'
            'model = "gpt"\n'
        )
        self.assertEqual(parsed["model"], "gpt")


if __name__ == "__main__":
    unittest.main()
