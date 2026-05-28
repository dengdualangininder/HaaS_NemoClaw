# HANDOFF

## Goal

讓 NemoClaw / OpenClaw 可以打開 browser，操作 HaaS NemoClaw dashboard，完整跑完 HaaS marketplace ops demo，讓團隊可以螢幕錄影。

錄影要呈現：

- NemoClaw 像長程營運代理一樣審核 public help signals。
- 它能產生 HaaS task draft。
- 它會在 external outreach、finance rewrite、reward proposal 等高風險動作前建立 checkpoint。
- 它會拒絕 doxxing / confrontation / private contact data。
- 它能中斷後恢復，所有 run/checkpoint/event/report 都在 SQLite。
- 它可切換 offline `scripted_nemotron` 與可選 NVIDIA NIM / Nemotron backend。

## Current Branch

```text
codex/nemoclaw-long-agent
```

主要入口：

```bash
python3 main.py demo
python3 main.py demo --auto-answer
python3 main.py ui --host 0.0.0.0 --port 8765
python3 main.py guardrail-demo
```

## Browser Demo URL

Mac 本機：

```text
http://127.0.0.1:8765
```

NemoClaw / OpenClaw container 內通常使用：

```text
http://host.docker.internal:8765
```

若失敗，改用 Mac LAN IP：

```bash
ipconfig getifaddr en0
```

```text
http://<MAC_LAN_IP>:8765
```

## NemoClaw Sandbox Lifecycle

```bash
nemoclaw onboard
nemoclaw nemoclaw rebuild --yes
nemoclaw nemoclaw destroy --force
nemoclaw nemoclaw dashboard-url --quiet
```

## Identify Container

```bash
docker ps | grep nemoclaw
```

容器名格式類似：

```text
openshell-nemoclaw-6fd8bd69-76e6-42b1-b763-e8e677b40872
```

設定變數：

```bash
CONTAINER=openshell-nemoclaw-6fd8bd69-76e6-42b1-b763-e8e677b40872
```

## Optional Docker Network

```bash
docker network create nemoclaw-net
docker network connect nemoclaw-net "$CONTAINER"
```

`docker ...` 指令在 Mac shell 跑，不是在 container 的 `#` shell 跑。

## Test Container Internet

```bash
docker exec "$CONTAINER" \
  python3 -c "import urllib.request; print(urllib.request.urlopen('https://example.com', timeout=5).status)"
```

外網不是 offline demo 必需；只有 live NIM backend 需要。

## Test Container Can Reach Dashboard

Mac 端啟動：

```bash
cd "/Users/user/Desktop/程式碼/2026Nvidia/Haas-Nvidia (1)"
python3 main.py ui --host 0.0.0.0 --port 8765
```

另開 Mac shell 測：

```bash
docker exec "$CONTAINER" \
  python3 -c "import urllib.request; r=urllib.request.urlopen('http://host.docker.internal:8765', timeout=5); print(r.status, r.headers.get('content-type'))"
```

預期：

```text
200 text/html
```

## Copy Project Into Container

```bash
docker exec "$CONTAINER" mkdir -p /workspace/haas-nemoclaw
docker cp "/Users/user/Desktop/程式碼/2026Nvidia/Haas-Nvidia (1)/." \
  "$CONTAINER":/workspace/haas-nemoclaw
```

進 container：

```bash
docker exec -it "$CONTAINER" sh
```

容器內：

```bash
cd /workspace/haas-nemoclaw
python3 main.py demo --auto-answer
python3 main.py guardrail-demo
```

## OpenClaw Prompt

```text
Open http://host.docker.internal:8765.
Operate the HaaS NemoClaw dashboard as a long-agent marketplace ops admin.
Start a demo run, inspect the first pending checkpoint, submit an operator decision, resume the run, and repeat until the final HaaS ops report appears.
Show the event log, guardrail interventions, and checkpoint persistence.
If NVIDIA NIM is available, switch inference to NVIDIA NIM and select a Nemotron model; otherwise use Offline Nemotron Script.
```

## Manual Recording Flow

1. Open dashboard.
2. Click `Start Demo Run`.
3. Inspect the run detail and right-side checkpoint.
4. Submit `approve-draft-only-invite`.
5. Click `Resume Run`.
6. Submit finance rewrite checkpoint.
7. Submit reward proposal-only checkpoint.
8. Show final `HaaS Ops Actions` report.
9. Run `guardrail-demo` in terminal if the recording needs direct policy proof.

## If OpenClaw Looks Stuck

1. Confirm Mac browser can open `http://127.0.0.1:8765`.
2. Confirm container can fetch `http://host.docker.internal:8765`.
3. If `host.docker.internal` fails, use Mac LAN IP.
4. If the URL works from container but OpenClaw still stalls, check whether the OpenClaw browser/control tool is enabled.
