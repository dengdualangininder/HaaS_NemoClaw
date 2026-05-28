# HaaS NemoClaw Long Agent

## 繁體中文

HaaS NemoClaw Long Agent 是一個專為 NemoClaw / OpenClaw 受限環境設計的離線優先 marketplace operations 長程代理。

它解決一個具體工作流：

> 將公開社群中的求助訊號轉成安全的 HaaS 任務草稿；在外部聯絡或 payout 相關動作前暫停並要求人工核准；把狀態持久化；中斷後可恢復；最後產生可審計的營運報告，而且不需要任意連網或讀取 host 檔案。

## HaaS 是什麼

HaaS 代表 **Human as a Service**：一個把真人經驗、在地知識、主觀判斷與小型協作需求轉成可驗收任務的市場。

一般 AI agent 很會生成文字，但它不能真的品嚐食物、確認在地語感、提供親身經驗、替社群需求做真人判斷，也不應該在高風險場景中自動聯絡外部使用者或移動資金。HaaS 的核心想法是：讓 AI 負責任務營運與安全審核，讓真人提供 AI 無法可靠取得的脈絡與經驗。

HaaS 裡有幾個角色：

- **Requester**：提出需求的人，例如想知道某個味覺描述、在地用語、產品感受或社群協作需求。
- **Hunter / Contributor**：完成任務的人，提供真人回答、觀察、脈絡或驗證。
- **NemoClaw Ops Agent**：後台長程代理，負責發現需求、整理任務、套用 guardrails、建立 checkpoint、產生 reward proposal 與 audit log。
- **Human Operator**：在外部聯絡、payout、高風險任務或政策模糊時做最終核准。

## HaaS 如何運作

HaaS 的營運邏輯是把「模糊的公開訊號」變成「可執行、可驗收、可審計的任務」：

```text
public help signal
  -> NemoClaw reviews the signal
  -> classify category and risk
  -> draft a HaaS quest
  -> apply policy-based guardrails
  -> create human checkpoint if needed
  -> requester/operator approval
  -> contributor submission
  -> verification
  -> reward proposal
  -> audit log and ops report
```

例如：

- 「黑巧克力配辣椒，辣椒要有青青的香氣」可以變成低風險感官任務，邀請真人描述味覺差異。
- 「找出某人的住址電話去堵他」會被拒絕，因為涉及 doxxing、騷擾與安全風險。
- 「告訴我明天買哪支股票並保證獲利」會被改寫成一般教育型市場風險討論，不能提供個人化買賣建議。
- 「要發 reward」只能產生 proposal，不能自動移動真實資金。

這個 repo 展示的是 HaaS 的 **後台長程營運代理**，不是完整金流或外部社群平台整合。重點在於讓 NemoClaw 能穩定執行長任務、保存狀態、遇到風險時停下來，並留下可審計紀錄。

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

## What Is HaaS

HaaS means **Human as a Service**: a marketplace that turns human experience, local knowledge, subjective judgment, and small collaborative requests into verifiable tasks.

AI agents are good at generating text, but they cannot actually taste food, verify local nuance, provide lived experience, or safely make every social judgment. They also should not automatically contact external users or move funds in high-risk situations. HaaS lets AI handle task operations and safety review while humans provide the context and experience that models cannot reliably obtain.

Core roles:

- **Requester:** the person or system asking for help.
- **Hunter / Contributor:** the human who completes the task with experience, observation, context, or verification.
- **NemoClaw Ops Agent:** the long-running backend agent that reviews signals, drafts tasks, applies guardrails, creates checkpoints, proposes rewards, and writes audit logs.
- **Human Operator:** the approver for external outreach, payout-sensitive actions, high-risk tasks, or ambiguous policy decisions.

## How HaaS Works

HaaS turns messy public signals into executable, verifiable, auditable tasks:

```text
public help signal
  -> NemoClaw reviews the signal
  -> classify category and risk
  -> draft a HaaS quest
  -> apply policy-based guardrails
  -> create human checkpoint if needed
  -> requester/operator approval
  -> contributor submission
  -> verification
  -> reward proposal
  -> audit log and ops report
```

Examples:

- A post about “dark chocolate with fresh green chili aroma” can become a low-risk sensory bounty.
- A request to find someone’s address and confront them is refused as doxxing / harassment / safety risk.
- A request for exact stock picks with guaranteed profit is rewritten into general educational market-risk discussion.
- A reward action becomes a proposal only; real funds are never moved automatically.

This repo demonstrates the **long-running backend operations agent** for HaaS, not a full payment system or live social-platform integration. The focus is persistence, checkpoints, guardrails, repeatable execution, and auditable ops behavior inside NemoClaw.

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
