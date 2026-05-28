from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from haas_nemoclaw.models import CheckpointRecord, RunState
from haas_nemoclaw.store import SQLiteStore


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliIntegrationTests(unittest.TestCase):
    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        command = ["python3", "main.py", *args]
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=merged_env,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_demo_auto_answer_cli_completes_and_reports(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "cli.db")
            demo = self.run_cli("--db", db_path, "demo", "--auto-answer")
            self.assertIn("status: completed", demo.stdout)

            run_id = next(
                line.split(": ", 1)[1]
                for line in demo.stdout.splitlines()
                if line.startswith("run_id:")
            )
            report = self.run_cli("--db", db_path, "report", "--run-id", run_id)
            self.assertIn("HaaS Ops Actions", report.stdout)

    def test_status_and_report_do_not_require_nim_credentials_for_existing_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "nim.db"
            store = SQLiteStore(db_path)
            run_state = RunState(
                run_id="run-nimstub",
                scenario_id="haas_ops_marketplace",
                title="NIM Metadata Compatibility",
                objective="Ensure read-only CLI commands do not require NIM credentials.",
                status="completed",
                phase="completed",
                clause_index=4,
                plan=[],
                findings=[],
                reasoner_backend="nim",
                target_model="nvidia/llama-3.3-nemotron-super-49b-v1",
                inference_base_url="https://integrate.api.nvidia.com/v1",
                auto_answer=False,
                final_report="stub report",
                metrics={},
            )
            store.create_run(run_state)

            env = {"NVIDIA_API_KEY": ""}
            status = self.run_cli("--db", str(db_path), "status", "--run-id", run_state.run_id, env=env)
            report = self.run_cli("--db", str(db_path), "report", "--run-id", run_state.run_id, env=env)

            self.assertIn("run_id: run-nimstub", status.stdout)
            self.assertIn("stub report", report.stdout)

    def test_answer_does_not_require_nim_credentials_for_existing_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "nim_answer.db"
            store = SQLiteStore(db_path)
            store.create_run(
                RunState(
                    run_id="run-nimanswer",
                    scenario_id="haas_ops_marketplace",
                    title="NIM Answer Compatibility",
                    objective="Ensure checkpoint answers do not require NIM credentials.",
                    status="waiting_human",
                    phase="waiting_human",
                    clause_index=1,
                    plan=[],
                    findings=[],
                    reasoner_backend="nim",
                    target_model="nvidia/llama-3.3-nemotron-super-49b-v1",
                    inference_base_url="https://integrate.api.nvidia.com/v1",
                    auto_answer=False,
                    final_report="",
                    metrics={},
                )
            )
            store.create_checkpoint(
                checkpoint=CheckpointRecord(
                    checkpoint_id="cp-nimanswer",
                    run_id="run-nimanswer",
                    clause_id="lead_outreach_002",
                    title="Invite Original Author to Confirm Task",
                    question="Choose a decision.",
                    options=["approve-draft-only-invite", "hold-for-manual-review"],
                )
            )

            env = {"NVIDIA_API_KEY": ""}
            answer = self.run_cli(
                "--db",
                str(db_path),
                "answer",
                "--run-id",
                "run-nimanswer",
                "--checkpoint-id",
                "cp-nimanswer",
                "--decision",
                "approve-draft-only-invite",
                env=env,
            )

            self.assertIn("Answered checkpoint cp-nimanswer", answer.stdout)


if __name__ == "__main__":
    unittest.main()
