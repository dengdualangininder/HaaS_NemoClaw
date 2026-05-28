# HaaS NemoClaw Long Agent

## 繁體中文

HaaS NemoClaw Long Agent 是一個專為 NemoClaw / OpenClaw 受限環境設計的離線優先 marketplace operations 長程代理。

它解決一個具體工作流：

> 將公開社群中的求助訊號轉成安全的 HaaS 任務草稿；在外部聯絡或 payout 相關動作前暫停並要求人工核准；把狀態持久化；中斷後可恢復；最後產生可審計的營運報告，而且不需要任意連網或讀取 host 檔案。

## 為什麼是這個問題

HaaS 是一個人類任務市場。真正困難的營運問題不是只生成任務文字，而是安全地把混亂的公開訊號轉成可執行任務，同時保留審核閘門。

這個 agent 可以：

- 審核內建的 public help signals。
- 產生低風險 HaaS quest 草稿。
- 拒絕 doxxing、stalking、confrontation、私人資料請求。
- 將個人化金融建議改寫成一般教育型市場風險討論。
- 在 external outreach 或 reward-sensitive actions 前暫停並要求人工核准。
- 將 runs、checkpoints、audit events、final reports 持久化到 SQLite。

## 競賽重點

- **實作價值：** HaaS marketplace lead triage 與任務營運。
- **長程自主性：** planning、analysis、pause、resume、completion。
- **持久性：** SQLite 保存 runs、checkpoints、events、reports。
- **穩定性：** 預設 demo 是 deterministic offline path，只使用 Python standard library。
- **安全性：** policy layer 會拒絕 unsafe actions，並將高風險自動化改寫成人工 checkpoint。
- **可部署性：** `python3 main.py ...` 可直接執行，不需安裝套件。

## NemoClaw-First 設計

預設 runtime 假設環境受限：

- 不任意連外網。
- 不任意讀取 host filesystem。
- 不需要安裝 package。
- 只在專案擁有的 runtime state 寫入資料。

因此 agent 使用：

- 內建 HaaS public-signal scenarios。
- 內建 operator policy defaults。
- SQLite app-owned state。
- reasoner adapter abstraction。

## Nemotron / NIM 整合模型

支援兩種 reasoner backend：

1. `scripted_nemotron`
   - 受限 NemoClaw demo 的預設 backend。
   - 完全離線且 deterministic。
   - 輸出與 live backend 相同的 planning、lead-analysis、checkpoint、report contract。

2. `nim`
   - 在允許連網時可使用的 live backend。
   - 透過 NVIDIA NIM 的 OpenAI-compatible `POST /v1/chat/completions` endpoint。
   - 從環境變數或 dashboard connection form 讀取 credentials。

離線 demo 不假裝真的呼叫 live Nemotron。它用 deterministic outputs 展示相同的 state machine 與 guardrail contract，讓評審能在受限 sandbox 中穩定重播。

## 核心流程

```text
public signal queue
  -> plan HaaS ops review
  -> analyze leads one by one
  -> guardrail intercepts outreach / payout / finance / privacy risk
  -> create human checkpoint when approval is required
  -> persist run + audit log
  -> resume after answer
  -> synthesize final HaaS ops report
```

## 專案結構

- `main.py`：CLI entrypoint。
- `main.py ui`：local visual dashboard entrypoint。
- `haas_nemoclaw/engine.py`：long-agent state machine。
- `haas_nemoclaw/dashboard.py`：local HTTP dashboard and runtime API。
- `haas_nemoclaw/guardrails.py`：policy-based guardrails。
- `haas_nemoclaw/reasoners.py`：offline and NIM-backed reasoners。
- `haas_nemoclaw/store.py`：SQLite persistence。
- `haas_nemoclaw/scenarios.py`：bundled HaaS ops scenarios。
- `SETUP.md`：NemoClaw setup。
- `DEMO.md`：exact demo commands。
- `ARCHITECTURE.md`：runtime design。
- `SAFETY.md`：implemented guardrails and failure modes。
- `SUBMISSION.md`：judge-facing one-pager。

## 快速開始

受限環境 demo：

```bash
python3 main.py demo
```

視覺化 dashboard：

```bash
python3 main.py ui --port 8765
```

開啟：

```text
http://127.0.0.1:8765
```

無人工介入完整執行：

```bash
python3 main.py demo --auto-answer
```

Guardrail 展示：

```bash
python3 main.py guardrail-demo
```

## 操作流程範例

1. 建立 run：

```bash
python3 main.py demo
```

2. 查看暫停狀態：

```bash
python3 main.py status --run-id <RUN_ID>
```

3. 回答 checkpoint：

```bash
python3 main.py answer \
  --run-id <RUN_ID> \
  --checkpoint-id <CHECKPOINT_ID> \
  --decision approve-draft-only-invite \
  --notes "Keep outreach as a draft until HaaS Ops approves the connector path."
```

4. 恢復執行：

```bash
python3 main.py run --run-id <RUN_ID>
```

5. 輸出報告：

```bash
python3 main.py report --run-id <RUN_ID>
```

## Live NIM 使用方式

若環境允許連網：

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```

Dashboard 也支援切換到 `NVIDIA NIM`、輸入 API key、選擇 Nemotron model，然後開始 live run。API key 只保存在 process memory，不會寫入 SQLite。

## 驗證

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Legacy Assets

歷史 HTML/JSX demos 保留在 `legacy/`。它們是背景展示素材；目前主要 NemoClaw submission path 是 SQLite-backed Long Agent runtime 與 dashboard。

---

## English

HaaS NemoClaw Long Agent is an offline-first marketplace-operations agent tailored for restricted NemoClaw / OpenClaw environments.

It solves one concrete workflow:

> Turn public help signals into safe HaaS task drafts, pause before external outreach or payout-sensitive actions, persist state durably, resume after interruption, and produce an auditable ops report without arbitrary web browsing or host-file access.

## Why This Problem

HaaS is a human task marketplace. The hard operational problem is not simply generating task text; it is safely turning messy public signals into actionable tasks while preserving review gates.

The agent can:

- Review bundled public help signals.
- Draft low-risk HaaS quests.
- Reject doxxing, stalking, confrontation, or private-data requests.
- Rewrite personalized financial advice into general educational risk discussion.
- Pause for human approval before external outreach or reward-sensitive actions.
- Persist runs, checkpoints, audit events, and final reports in SQLite.

## Competition Fit

- **Real problem-solving:** HaaS marketplace lead triage and task operations.
- **Long-running autonomy:** plan, analyze, pause, resume, complete.
- **Persistence:** SQLite-backed runs, checkpoints, events, and reports.
- **Stability:** deterministic offline demo path with Python standard library only.
- **Guardrails:** policy layer rejects unsafe actions and rewrites risky autonomy into checkpoints.
- **Deployability:** `python3 main.py ...` works without package installation.

## NemoClaw-First Design

The default runtime assumes a constrained environment:

- No arbitrary internet access.
- No arbitrary host filesystem reads.
- No package installation.
- Only project-owned runtime state is written locally.

Instead of reaching outside the sandbox, the agent uses:

- Bundled HaaS public-signal scenarios.
- Bundled operator policy defaults.
- SQLite state owned by this app.
- A reasoner adapter abstraction.

## Nemotron / NIM Integration Model

Two reasoner backends are supported:

1. `scripted_nemotron`
   - Default for restricted NemoClaw demos.
   - Fully offline and deterministic.
   - Emits the same planning, lead-analysis, checkpoint, and report contract as the live backend.

2. `nim`
   - Optional live backend for environments that can reach NVIDIA NIM.
   - Uses an OpenAI-compatible `POST /v1/chat/completions` endpoint.
   - Reads credentials from environment variables or the dashboard connection form.

The offline demo does not pretend to call live Nemotron. It demonstrates the same state-machine and guardrail contract with deterministic outputs so judges can replay it inside restricted sandboxes.

## Core Flow

```text
public signal queue
  -> plan HaaS ops review
  -> analyze leads one by one
  -> guardrail intercepts outreach / payout / finance / privacy risk
  -> create human checkpoint when approval is required
  -> persist run + audit log
  -> resume after answer
  -> synthesize final HaaS ops report
```

## Repository Guide

- `main.py`: CLI entrypoint.
- `main.py ui`: local visual dashboard entrypoint.
- `haas_nemoclaw/engine.py`: long-agent state machine.
- `haas_nemoclaw/dashboard.py`: local HTTP dashboard and runtime API.
- `haas_nemoclaw/guardrails.py`: policy-based guardrails.
- `haas_nemoclaw/reasoners.py`: offline and NIM-backed reasoners.
- `haas_nemoclaw/store.py`: SQLite persistence.
- `haas_nemoclaw/scenarios.py`: bundled HaaS ops scenarios.
- `SETUP.md`: setup for NemoClaw.
- `DEMO.md`: exact demo commands.
- `ARCHITECTURE.md`: runtime design.
- `SAFETY.md`: implemented guardrails and failure modes.
- `SUBMISSION.md`: judge-facing one-pager.

## Quick Start

Restricted-environment demo:

```bash
python3 main.py demo
```

Visual dashboard:

```bash
python3 main.py ui --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

Unattended proof:

```bash
python3 main.py demo --auto-answer
```

Guardrail proof:

```bash
python3 main.py guardrail-demo
```

## Example Operator Flow

1. Start a run:

```bash
python3 main.py demo
```

2. Inspect paused state:

```bash
python3 main.py status --run-id <RUN_ID>
```

3. Answer the checkpoint:

```bash
python3 main.py answer \
  --run-id <RUN_ID> \
  --checkpoint-id <CHECKPOINT_ID> \
  --decision approve-draft-only-invite \
  --notes "Keep outreach as a draft until HaaS Ops approves the connector path."
```

4. Resume:

```bash
python3 main.py run --run-id <RUN_ID>
```

5. Print report:

```bash
python3 main.py report --run-id <RUN_ID>
```

## Live NIM Usage

If networking is allowed:

```bash
export NVIDIA_API_KEY="<your-key>"
python3 main.py demo --reasoner nim --nim-model nvidia/nemotron-3-super-120b-a12b
```

The dashboard also supports switching to `NVIDIA NIM`, entering an API key, selecting a Nemotron model, and starting a live run. The key is kept in process memory and is not written to SQLite.

## Verification

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Legacy Assets

Historical HTML/JSX demos are preserved under `legacy/`. They are background material; the primary NemoClaw submission path is the SQLite-backed Long Agent runtime and dashboard.
