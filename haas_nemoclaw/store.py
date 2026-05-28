from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from haas_nemoclaw.models import CheckpointRecord, RunState


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SQLiteStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _initialize(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    reasoner_backend TEXT NOT NULL,
                    target_model TEXT NOT NULL,
                    auto_answer INTEGER NOT NULL,
                    state_json TEXT NOT NULL,
                    final_report TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    clause_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    question TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    decision TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    ts TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    message TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def create_run(self, run_state: RunState) -> None:
        now = utc_now()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO runs (
                    run_id, scenario_id, status, phase, reasoner_backend, target_model,
                    auto_answer, state_json, final_report, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_state.run_id,
                    run_state.scenario_id,
                    run_state.status,
                    run_state.phase,
                    run_state.reasoner_backend,
                    run_state.target_model,
                    int(run_state.auto_answer),
                    json.dumps(run_state.to_dict(), ensure_ascii=True),
                    run_state.final_report,
                    now,
                    now,
                ),
            )

    def save_run(self, run_state: RunState) -> None:
        now = utc_now()
        with self._connect() as con:
            con.execute(
                """
                UPDATE runs
                SET status = ?, phase = ?, reasoner_backend = ?, target_model = ?,
                    auto_answer = ?, state_json = ?, final_report = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (
                    run_state.status,
                    run_state.phase,
                    run_state.reasoner_backend,
                    run_state.target_model,
                    int(run_state.auto_answer),
                    json.dumps(run_state.to_dict(), ensure_ascii=True),
                    run_state.final_report,
                    now,
                    run_state.run_id,
                ),
            )

    def get_run(self, run_id: str) -> RunState:
        with self._connect() as con:
            row = con.execute("SELECT state_json FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"Run not found: {run_id}")
        return RunState.from_dict(json.loads(row["state_json"]))

    def list_runs(self) -> list[dict[str, str]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT run_id, scenario_id, status, phase, reasoner_backend, updated_at
                FROM runs ORDER BY updated_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def create_checkpoint(self, checkpoint: CheckpointRecord) -> None:
        now = utc_now()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO checkpoints (
                    checkpoint_id, run_id, clause_id, title, question, options_json,
                    status, decision, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checkpoint.checkpoint_id,
                    checkpoint.run_id,
                    checkpoint.clause_id,
                    checkpoint.title,
                    checkpoint.question,
                    json.dumps(checkpoint.options, ensure_ascii=True),
                    checkpoint.status,
                    checkpoint.decision,
                    checkpoint.notes,
                    now,
                    now,
                ),
            )

    def save_checkpoint(self, checkpoint: CheckpointRecord) -> None:
        now = utc_now()
        with self._connect() as con:
            con.execute(
                """
                UPDATE checkpoints
                SET status = ?, decision = ?, notes = ?, updated_at = ?
                WHERE checkpoint_id = ?
                """,
                (
                    checkpoint.status,
                    checkpoint.decision,
                    checkpoint.notes,
                    now,
                    checkpoint.checkpoint_id,
                ),
            )

    def get_checkpoint(self, checkpoint_id: str) -> CheckpointRecord:
        with self._connect() as con:
            row = con.execute(
                """
                SELECT checkpoint_id, run_id, clause_id, title, question, options_json,
                       status, decision, notes
                FROM checkpoints WHERE checkpoint_id = ?
                """,
                (checkpoint_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Checkpoint not found: {checkpoint_id}")
        return CheckpointRecord(
            checkpoint_id=row["checkpoint_id"],
            run_id=row["run_id"],
            clause_id=row["clause_id"],
            title=row["title"],
            question=row["question"],
            options=json.loads(row["options_json"]),
            status=row["status"],
            decision=row["decision"],
            notes=row["notes"],
        )

    def list_checkpoints(self, run_id: str) -> list[CheckpointRecord]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT checkpoint_id, run_id, clause_id, title, question, options_json,
                       status, decision, notes
                FROM checkpoints
                WHERE run_id = ?
                ORDER BY created_at ASC
                """,
                (run_id,),
            ).fetchall()
        return [
            CheckpointRecord(
                checkpoint_id=row["checkpoint_id"],
                run_id=row["run_id"],
                clause_id=row["clause_id"],
                title=row["title"],
                question=row["question"],
                options=json.loads(row["options_json"]),
                status=row["status"],
                decision=row["decision"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def count_open_checkpoints(self, run_id: str) -> int:
        with self._connect() as con:
            row = con.execute(
                "SELECT COUNT(*) AS total FROM checkpoints WHERE run_id = ? AND status != 'answered'",
                (run_id,),
            ).fetchone()
        return int(row["total"])

    def add_event(self, run_id: str, kind: str, message: str, payload: dict) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO events (run_id, ts, kind, message, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, utc_now(), kind, message, json.dumps(payload, ensure_ascii=True)),
            )

    def list_events(self, run_id: str) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT ts, kind, message, payload_json FROM events WHERE run_id = ? ORDER BY id ASC",
                (run_id,),
            ).fetchall()
        return [
            {
                "ts": row["ts"],
                "kind": row["kind"],
                "message": row["message"],
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]
