from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from haas_nemoclaw.engine import LongAgentEngine
from haas_nemoclaw.guardrails import GuardrailPolicy, demo_operations
from haas_nemoclaw.reasoners import ScriptedNemotronReasoner
from haas_nemoclaw.scenarios import DEMO_SCENARIO
from haas_nemoclaw.store import SQLiteStore


class LongAgentTests(unittest.TestCase):
    def make_engine(self, temp_dir: str):
        store = SQLiteStore(Path(temp_dir) / "runtime.db")
        engine = LongAgentEngine(
            store=store,
            reasoner=ScriptedNemotronReasoner(),
            guardrails=GuardrailPolicy(),
        )
        return store, engine

    def test_run_persists_and_resumes_across_checkpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store, engine = self.make_engine(tmpdir)
            run_state = engine.create_run(DEMO_SCENARIO.scenario_id, auto_answer=False)
            run_state = engine.run_until_blocked(run_state.run_id)

            self.assertEqual(run_state.status, "waiting_human")
            checkpoints = store.list_checkpoints(run_state.run_id)
            self.assertEqual(len(checkpoints), 1)
            self.assertEqual(checkpoints[0].clause_id, "lead_outreach_002")

            # Simulate a restart with fresh runtime objects.
            store, engine = self.make_engine(tmpdir)
            engine.answer_checkpoint(
                run_state.run_id,
                checkpoints[0].checkpoint_id,
                "approve-draft-only-invite",
                "Keep outreach as a draft until HaaS Ops approves the connector path.",
            )

            run_state = engine.run_until_blocked(run_state.run_id)
            self.assertEqual(run_state.status, "waiting_human")
            checkpoints = store.list_checkpoints(run_state.run_id)
            self.assertEqual(len(checkpoints), 2)
            self.assertEqual(checkpoints[1].clause_id, "lead_finance_004")

    def test_auto_answer_reaches_completion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store, engine = self.make_engine(tmpdir)
            run_state = engine.create_run(DEMO_SCENARIO.scenario_id, auto_answer=True)
            run_state = engine.run_until_blocked(run_state.run_id)

            self.assertEqual(run_state.status, "completed")
            self.assertIn("HaaS Ops Actions", run_state.final_report)
            self.assertGreaterEqual(store.count_open_checkpoints(run_state.run_id), 0)

    def test_guardrails_reject_and_rewrite_expected_operations(self):
        policy = GuardrailPolicy()
        decisions = [policy.evaluate(operation) for operation in demo_operations()]
        verdicts = [decision.verdict for decision in decisions]
        self.assertEqual(verdicts, ["reject", "reject", "rewrite", "reject"])

    def test_invalid_checkpoint_decision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, engine = self.make_engine(tmpdir)
            run_state = engine.create_run(DEMO_SCENARIO.scenario_id, auto_answer=False)
            run_state = engine.run_until_blocked(run_state.run_id)
            checkpoint_id = engine.store.list_checkpoints(run_state.run_id)[0].checkpoint_id

            with self.assertRaises(ValueError):
                engine.answer_checkpoint(
                    run_state.run_id,
                    checkpoint_id,
                    "unsupported-decision",
                    "bad option",
                )


if __name__ == "__main__":
    unittest.main()
