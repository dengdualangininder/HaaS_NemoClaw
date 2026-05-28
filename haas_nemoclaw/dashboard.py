from __future__ import annotations

import json
import os
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Callable
from urllib.parse import urlparse

from haas_nemoclaw.engine import LongAgentEngine
from haas_nemoclaw.guardrails import GuardrailPolicy
from haas_nemoclaw.reasoners import (
    DEFAULT_NIM_BASE_URL,
    DEFAULT_NIM_MODEL,
    build_reasoner,
    fetch_nim_models,
    probe_nim_connection,
    recommended_nim_models,
)
from haas_nemoclaw.scenarios import DEMO_SCENARIO, get_scenario
from haas_nemoclaw.store import SQLiteStore


@dataclass
class NimRuntimeSnapshot:
    connected: bool
    source: str
    model_name: str
    base_url: str
    key_present: bool
    key_hint: str
    models: list[str]

    def to_dict(self) -> dict:
        return {
            "connected": self.connected,
            "source": self.source,
            "model_name": self.model_name,
            "base_url": self.base_url,
            "key_present": self.key_present,
            "key_hint": self.key_hint,
            "models": list(self.models),
        }


class NimRuntimeConfig:
    def __init__(self, default_model: str, default_base_url: str = DEFAULT_NIM_BASE_URL):
        self._lock = Lock()
        self._default_model = default_model
        self._default_base_url = default_base_url
        self._recommended_models = recommended_nim_models()
        self._env_api_key = os.getenv("NVIDIA_API_KEY", "").strip()
        self._env_base_url = os.getenv("NIM_BASE_URL", default_base_url).strip() or default_base_url
        self._session_api_key = ""
        self._session_base_url = default_base_url
        self._session_model = default_model
        self._available_models = list(self._recommended_models)

    def snapshot(self) -> NimRuntimeSnapshot:
        with self._lock:
            api_key = self._session_api_key or self._env_api_key
            source = "session" if self._session_api_key else ("env" if self._env_api_key else "none")
            model_name = self._session_model or self._default_model
            base_url = self._session_base_url or self._env_base_url or self._default_base_url
            models = _merge_model_lists(
                self._available_models,
                [model_name],
                self._recommended_models,
            )
        return NimRuntimeSnapshot(
            connected=bool(api_key),
            source=source,
            model_name=model_name,
            base_url=base_url,
            key_present=bool(api_key),
            key_hint=_mask_api_key(api_key),
            models=models,
        )

    def connect(
        self,
        api_key: str,
        model_name: str,
        base_url: str,
        *,
        probe_fn: Callable[[str, str, str], dict[str, str]],
        model_fetch_fn: Callable[[str, str], list[str]],
    ) -> NimRuntimeSnapshot:
        normalized_key = api_key.strip()
        normalized_model = model_name.strip() or self._default_model
        normalized_base_url = base_url.strip().rstrip("/") or self._default_base_url
        if not normalized_key:
            raise RuntimeError("NVIDIA API key is required.")
        probe_fn(normalized_key, normalized_model, normalized_base_url)
        available_models = model_fetch_fn(normalized_key, normalized_base_url)
        with self._lock:
            self._session_api_key = normalized_key
            self._session_model = normalized_model
            self._session_base_url = normalized_base_url
            self._available_models = _merge_model_lists(
                available_models,
                [normalized_model],
                self._recommended_models,
            )
        return self.snapshot()

    def disconnect(self) -> NimRuntimeSnapshot:
        with self._lock:
            self._session_api_key = ""
            self._session_model = self._default_model
            self._session_base_url = self._default_base_url
            self._available_models = list(self._recommended_models)
        return self.snapshot()

    def credentials_for(self, model_name: str | None = None, base_url: str | None = None) -> dict[str, str]:
        snapshot = self.snapshot()
        if not snapshot.key_present:
            raise RuntimeError("Connect NVIDIA NIM first or export NVIDIA_API_KEY before using the nim backend.")
        return {
            "api_key": self._session_api_key or self._env_api_key,
            "model_name": (model_name or snapshot.model_name).strip() or snapshot.model_name,
            "base_url": (base_url or snapshot.base_url).strip().rstrip("/") or snapshot.base_url,
        }


def serve_dashboard(
    db_path: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    default_reasoner: str = "scripted_nemotron",
    nim_model: str = DEFAULT_NIM_MODEL,
) -> None:
    server = create_dashboard_server(
        db_path=db_path,
        host=host,
        port=port,
        default_reasoner=default_reasoner,
        nim_model=nim_model,
    )
    print(f"Dashboard running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def create_dashboard_server(
    db_path: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    default_reasoner: str = "scripted_nemotron",
    nim_model: str = DEFAULT_NIM_MODEL,
    *,
    nim_probe: Callable[[str, str, str], dict[str, str]] = probe_nim_connection,
    nim_model_fetcher: Callable[[str, str], list[str]] = fetch_nim_models,
    reasoner_builder: Callable[..., object] = build_reasoner,
) -> ThreadingHTTPServer:
    store = SQLiteStore(db_path)
    nim_runtime = NimRuntimeConfig(default_model=nim_model)
    return ThreadingHTTPServer(
        (host, port),
        _build_handler(
            store=store,
            default_reasoner=default_reasoner,
            nim_model=nim_model,
            nim_runtime=nim_runtime,
            nim_probe=nim_probe,
            nim_model_fetcher=nim_model_fetcher,
            reasoner_builder=reasoner_builder,
        ),
    )


def _build_handler(
    store: SQLiteStore,
    default_reasoner: str,
    nim_model: str,
    nim_runtime: NimRuntimeConfig,
    nim_probe: Callable[[str, str, str], dict[str, str]],
    nim_model_fetcher: Callable[[str, str], list[str]],
    reasoner_builder: Callable[..., object],
):
    web_root = Path(__file__).resolve().parents[1] / "web_ui"

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                return self._serve_static("index.html", "text/html; charset=utf-8")
            if parsed.path == "/app.js":
                return self._serve_static("app.js", "application/javascript; charset=utf-8")
            if parsed.path == "/dashboard.css":
                return self._serve_static("dashboard.css", "text/css; charset=utf-8")
            if parsed.path == "/api/runtime":
                return self._json_response(self._runtime_payload())
            if parsed.path == "/api/runs":
                return self._json_response(
                    {
                        "runs": [_serialize_run_summary(row) for row in store.list_runs()],
                        "runtime": self._runtime_payload()["runtime"],
                    }
                )
            if parsed.path.startswith("/api/runs/"):
                return self._handle_run_get(parsed.path)
            return self._json_response({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            try:
                payload = self._read_json_body()
                if parsed.path == "/api/runs":
                    return self._handle_create_run(payload)
                if parsed.path == "/api/nim/connect":
                    return self._handle_nim_connect(payload)
                if parsed.path == "/api/nim/disconnect":
                    return self._handle_nim_disconnect()
                if parsed.path.startswith("/api/runs/") and parsed.path.endswith("/resume"):
                    run_id = parsed.path.split("/")[3]
                    return self._handle_resume_run(run_id)
                if parsed.path.startswith("/api/checkpoints/") and parsed.path.endswith("/answer"):
                    checkpoint_id = parsed.path.split("/")[3]
                    return self._handle_answer_checkpoint(checkpoint_id, payload)
                return self._json_response({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            except RuntimeError as exc:
                return self._json_response({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

        def log_message(self, format: str, *args) -> None:
            return

        def _runtime_payload(self) -> dict:
            return {
                "runtime": {
                    "default_reasoner": default_reasoner,
                    "default_nim_model": nim_model,
                    "nim": nim_runtime.snapshot().to_dict(),
                }
            }

        def _handle_run_get(self, path: str) -> None:
            parts = path.strip("/").split("/")
            if len(parts) != 3:
                return self._json_response({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            run_id = parts[2]
            try:
                run_state = store.get_run(run_id)
            except KeyError as exc:
                return self._json_response({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
            detail = _serialize_run_detail(store, run_state)
            detail["runtime"] = self._runtime_payload()["runtime"]
            return self._json_response(detail)

        def _handle_create_run(self, payload: dict) -> None:
            scenario_id = payload.get("scenario_id", DEMO_SCENARIO.scenario_id)
            auto_answer = bool(payload.get("auto_answer", False))
            reasoner_backend = payload.get("reasoner", default_reasoner)
            model_name = payload.get("nim_model", nim_model)
            if reasoner_backend == "nim":
                credentials = nim_runtime.credentials_for(model_name=model_name)
                reasoner = reasoner_builder(
                    reasoner_backend,
                    model_name=credentials["model_name"],
                    api_key=credentials["api_key"],
                    base_url=credentials["base_url"],
                )
            else:
                reasoner = reasoner_builder(reasoner_backend, model_name=model_name)
            engine = LongAgentEngine(store=store, reasoner=reasoner, guardrails=GuardrailPolicy())
            run_state = engine.create_run(scenario_id, auto_answer=auto_answer)
            run_state = engine.run_until_blocked(run_state.run_id)
            detail = _serialize_run_detail(store, run_state)
            detail["runtime"] = self._runtime_payload()["runtime"]
            return self._json_response(detail, status=HTTPStatus.CREATED)

        def _handle_resume_run(self, run_id: str) -> None:
            try:
                existing = store.get_run(run_id)
            except KeyError as exc:
                return self._json_response({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)

            if existing.reasoner_backend == "nim":
                credentials = nim_runtime.credentials_for(
                    model_name=existing.target_model,
                    base_url=existing.inference_base_url,
                )
                reasoner = reasoner_builder(
                    existing.reasoner_backend,
                    model_name=credentials["model_name"],
                    api_key=credentials["api_key"],
                    base_url=credentials["base_url"],
                )
            else:
                reasoner = reasoner_builder(
                    existing.reasoner_backend,
                    model_name=existing.target_model,
                )

            engine = LongAgentEngine(store=store, reasoner=reasoner, guardrails=GuardrailPolicy())
            run_state = engine.run_until_blocked(run_id)
            detail = _serialize_run_detail(store, run_state)
            detail["runtime"] = self._runtime_payload()["runtime"]
            return self._json_response(detail)

        def _handle_answer_checkpoint(self, checkpoint_id: str, payload: dict) -> None:
            try:
                checkpoint = store.get_checkpoint(checkpoint_id)
            except KeyError as exc:
                return self._json_response({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
            decision = payload.get("decision", "")
            notes = payload.get("notes", "")
            engine = LongAgentEngine(store=store, reasoner=None, guardrails=GuardrailPolicy())
            try:
                engine.answer_checkpoint(checkpoint.run_id, checkpoint_id, decision, notes)
                run_state = store.get_run(checkpoint.run_id)
            except ValueError as exc:
                return self._json_response({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            detail = _serialize_run_detail(store, run_state)
            detail["runtime"] = self._runtime_payload()["runtime"]
            return self._json_response(detail)

        def _handle_nim_connect(self, payload: dict) -> None:
            snapshot = nim_runtime.connect(
                api_key=payload.get("api_key", ""),
                model_name=payload.get("model_name", nim_model),
                base_url=payload.get("base_url", DEFAULT_NIM_BASE_URL),
                probe_fn=nim_probe,
                model_fetch_fn=nim_model_fetcher,
            )
            return self._json_response({"nim": snapshot.to_dict()})

        def _handle_nim_disconnect(self) -> None:
            snapshot = nim_runtime.disconnect()
            return self._json_response({"nim": snapshot.to_dict()})

        def _serve_static(self, filename: str, content_type: str) -> None:
            target = web_root / filename
            if not target.exists():
                return self._json_response({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            body = target.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json_body(self) -> dict:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length == 0:
                return {}
            raw = self.rfile.read(content_length).decode("utf-8")
            if not raw.strip():
                return {}
            return json.loads(raw)

        def _json_response(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return DashboardHandler


def _serialize_run_summary(row: dict[str, str]) -> dict:
    return {
        "run_id": row["run_id"],
        "scenario_id": row["scenario_id"],
        "status": row["status"],
        "phase": row["phase"],
        "reasoner_backend": row["reasoner_backend"],
        "updated_at": row["updated_at"],
    }


def _serialize_run_detail(store: SQLiteStore, run_state) -> dict:
    scenario = get_scenario(run_state.scenario_id)
    checkpoints = store.list_checkpoints(run_state.run_id)
    events = store.list_events(run_state.run_id)
    pending = [checkpoint for checkpoint in checkpoints if checkpoint.status != "answered"]
    return {
        "run": run_state.to_dict(),
        "scenario": {
            "scenario_id": scenario.scenario_id,
            "title": scenario.title,
            "objective": scenario.objective,
            "clause_total": len(scenario.clauses),
        },
        "checkpoints": [checkpoint.to_dict() for checkpoint in checkpoints],
        "pending_checkpoints": [checkpoint.to_dict() for checkpoint in pending],
        "events": events,
        "next_step": _next_step_text(run_state.status, run_state.run_id, pending),
    }


def _next_step_text(status: str, run_id: str, pending_checkpoints: list) -> str:
    if status == "completed":
        return f"Run {run_id} is complete. Review the final report."
    if status == "waiting_human" and pending_checkpoints:
        return f"Run {run_id} is waiting for a checkpoint answer."
    return f"Run {run_id} can continue execution."


def _mask_api_key(api_key: str) -> str:
    normalized = api_key.strip()
    if not normalized:
        return ""
    if len(normalized) <= 8:
        return "*" * len(normalized)
    return f"{normalized[:5]}...{normalized[-4:]}"


def _merge_model_lists(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            merged.append(normalized)
    return merged
