from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODE_FILE = ROOT / "mode_arbiter_codex.md"


class ModePolicyPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = MODE_FILE.read_text(encoding="utf-8")

    def test_required_policy_blocks_are_present_once(self) -> None:
        required_content = {
            "codex_task_start_recon_policy": (
                "perform bounded reconnaissance",
                "Expand the problem space before collapsing it",
                "internally form at least 2 plausible framings",
            ),
            "codex_tool_calling_policy": (
                "Treat tool use as part of understanding",
                "Prefer high-information-gain tool calls",
                "reopen the frame and revise the chosen path",
            ),
            "codex_agent_policy": (
                "Do not spawn, delegate to, or depend on other agents",
                "unless the user explicitly asks for sub-agents",
                "is not permission to use other agents",
            ),
            "unfinished_task_and_closure_policy": (
                'do not propose "next steps"',
                "Never use advisory closure to mask unfinished work",
                "Never use a DUET label to disguise incomplete execution",
                "finish the current objective first",
            ),
            "operator_triggers": (
                "Choose REASONING and COLLAB independently",
                "HSFRM should become dominant",
                "HDPRM should become dominant",
            ),
            "done_criteria": (
                "unguided leapiness and over-literal lock-in",
                "premature closure and purposeless prolongation",
                "Preserve useful insight without presenting speculation as certainty",
                "In DELIVERY, keep the answer self-contained",
                "In DUET, surface only frontier material",
            ),
        }
        for name, phrases in required_content.items():
            with self.subTest(name=name):
                self.assertEqual(self.text.count(f"<{name}>"), 1)
                self.assertEqual(self.text.count(f"</{name}>"), 1)
                start = self.text.index(f"<{name}>")
                end = self.text.index(f"</{name}>", start)
                block = self.text[start:end]
                for phrase in phrases:
                    self.assertIn(phrase, block)

    def test_reasoning_modes_keep_selection_metadata(self) -> None:
        self.assertEqual(self.text.count("- Strengths:"), 2)
        self.assertEqual(self.text.count("- Risks:"), 2)
        self.assertEqual(self.text.count("- Best used when:"), 2)

    def test_closure_policy_explicitly_preserves_duet(self) -> None:
        self.assertIn(
            "A user-facing DUET turn may intentionally exchange selected "
            "unfinished frontier material",
            self.text,
        )
        self.assertIn(
            "The DUET exception is narrow",
            self.text,
        )

    def test_operator_triggers_do_not_collapse_collaboration_axis(self) -> None:
        self.assertIn("[MODE_AUTO]", self.text)
        self.assertIn("[MODE_REOPEN]", self.text)
        self.assertIn("[MODE_TIGHTEN]", self.text)
        self.assertGreaterEqual(self.text.count("without forcing a COLLAB value"), 2)

    def test_additional_delivery_guardrails_are_preserved(self) -> None:
        required_phrases = (
            "Only force a specific order if the task itself makes that necessary.",
            "You may revise either axis if later understanding materially changes",
            "Prefer the lightest reasoning and collaboration posture",
            "Treat language as the surface realization of a deeper internal model",
            "In DELIVERY, prefer one best answer over a menu of options",
            "In DELIVERY, always provide a usable final answer",
            "Keep the mode block short",
            "Do not stack repeated hedges.",
            "In DELIVERY, mention alternatives only when ambiguity is central",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
