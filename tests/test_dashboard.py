from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib import request

from haas_nemoclaw.dashboard import create_dashboard_server
from haas_nemoclaw.reasoners import ScriptedNemotronReasoner


class FakeNimReasoner(ScriptedNemotronReasoner):
    def __init__(self, model_name: str, base_url: str):
        super().__init__(model_name=model_name)
        self.base_url = base_url

    def info(self):
        info = super().info()
        info.backend = "nim"
        info.base_url = self.base_url
        return info


class DashboardTests(unittest.TestCase):
    def test_dashboard_api_can_create_and_inspect_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                server = create_dashboard_server(
                    db_path=Path(tmpdir) / "dashboard.db",
                    host="127.0.0.1",
                    port=0,
                )
            except PermissionError:
                self.skipTest("Sandbox does not allow binding a local test port.")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_port}"
                runs_before = json.loads(request.urlopen(f"{base_url}/api/runs").read().decode("utf-8"))
                self.assertEqual(runs_before["runs"], [])

                payload = json.dumps({"scenario_id": "saas_vendor_msa", "auto_answer": False}).encode("utf-8")
                req = request.Request(
                    f"{base_url}/api/runs",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                created = json.loads(request.urlopen(req).read().decode("utf-8"))
                self.assertEqual(created["run"]["status"], "waiting_human")
                self.assertEqual(len(created["pending_checkpoints"]), 1)

                run_id = created["run"]["run_id"]
                detail = json.loads(request.urlopen(f"{base_url}/api/runs/{run_id}").read().decode("utf-8"))
                self.assertEqual(detail["run"]["run_id"], run_id)
                self.assertGreaterEqual(len(detail["events"]), 1)
                self.assertEqual(detail["run"]["inference_base_url"], "")
            finally:
                server.shutdown()
                server.server_close()

    def test_dashboard_can_connect_nim_and_create_live_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                server = create_dashboard_server(
                    db_path=Path(tmpdir) / "dashboard.db",
                    host="127.0.0.1",
                    port=0,
                    nim_probe=lambda api_key, model_name, base_url: {
                        "backend": "nim",
                        "model_name": model_name,
                        "base_url": base_url,
                        "probe_reply": "READY",
                    },
                    nim_model_fetcher=lambda api_key, base_url: [
                        "nvidia/llama-3.3-nemotron-super-49b-v1.5",
                        "meta/llama-3.1-8b-instruct",
                    ],
                    reasoner_builder=lambda backend, model_name, **kwargs: (
                        FakeNimReasoner(model_name=model_name, base_url=kwargs.get("base_url", ""))
                        if backend == "nim"
                        else ScriptedNemotronReasoner(model_name=model_name)
                    ),
                )
            except PermissionError:
                self.skipTest("Sandbox does not allow binding a local test port.")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_port}"

                connect_payload = json.dumps(
                    {
                        "api_key": "nvapi-demo-key",
                        "base_url": "https://integrate.api.nvidia.com/v1",
                        "model_name": "meta/llama-3.1-8b-instruct",
                    }
                ).encode("utf-8")
                connect_req = request.Request(
                    f"{base_url}/api/nim/connect",
                    data=connect_payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                connected = json.loads(request.urlopen(connect_req).read().decode("utf-8"))
                self.assertTrue(connected["nim"]["connected"])
                self.assertEqual(connected["nim"]["model_name"], "meta/llama-3.1-8b-instruct")

                payload = json.dumps(
                    {
                        "scenario_id": "saas_vendor_msa",
                        "auto_answer": False,
                        "reasoner": "nim",
                        "nim_model": "meta/llama-3.1-8b-instruct",
                    }
                ).encode("utf-8")
                req = request.Request(
                    f"{base_url}/api/runs",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                created = json.loads(request.urlopen(req).read().decode("utf-8"))
                self.assertEqual(created["run"]["reasoner_backend"], "nim")
                self.assertEqual(created["run"]["target_model"], "meta/llama-3.1-8b-instruct")
                self.assertEqual(
                    created["run"]["inference_base_url"],
                    "https://integrate.api.nvidia.com/v1",
                )
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
