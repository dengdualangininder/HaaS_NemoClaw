# HaaS NemoClaw Long Agent

這個專案已改寫為專為 NemoClaw 受限環境設計的 Long Agent 實作方案。核心目標不是展示聊天能力，而是展示一個可部署、可中斷恢復、可重複執行、具 policy-based guardrails 的長任務代理。

## 一句話

HaaS NemoClaw Long Agent 會把離線 public help signals 轉成安全、可驗收、可審核的任務草稿；遇到高風險需求會拒絕或改寫，並把每一步寫入持久化 state 與 audit log。

## 解決的問題定義

公開社群中有大量需要真人經驗、在地知識、主觀判斷或多人協作的需求，但它們通常沒有：

- 明確任務格式。
- 驗收規則。
- 安全審核。
- 跨回合狀態。
- reward / payout 提案與 audit trail。

本專案把問題縮成可實作、可衡量的競賽版本：

- 輸入：3 個內建離線 public signals。
- 輸出：安全任務草稿、拒絕紀錄或安全改寫。
- 衡量：每個 signal 都必須完成 state transition，且所有 durable operations 都保存到 `.nemoclaw/state.json`。
- 安全：外部聯絡與真實 payout 永遠只產生 draft/proposal，不自動執行。

## 快速啟動

不需要安裝依賴。

```bash
python3 main.py --mode demo
```

如果要做螢幕錄影，建議開啟瀏覽器營運版：

```bash
python3 -m http.server 8765
```

然後打開：

```text
http://127.0.0.1:8765/openclaw-ops.html
```

`openclaw-ops.html` 是 OpenClaw/NemoClaw 可操作的離線 Ops Console，可點選 scout lead、執行 policy review、draft、approve、verify、reward proposal、pause/resume，並在右側看到 audit log。

常用指令：

```bash
python3 main.py --mode reset
python3 main.py --mode status
python3 main.py --mode step
python3 main.py --mode resume
python3 main.py --mode policy-test
```

## Long Agent 任務拆解

任務 loop：

```text
offline signal
  -> scout.capture
  -> policy.evaluate
  -> quest.draft 或 guardrail.refuse
  -> verifier.accept
  -> reward.propose
  -> audit.write
  -> checkpoint
```

每次只推進一個最小 durable operation，然後立即保存 state。這讓任務不依賴模型上下文長度，也能在中斷後恢復。

## 狀態持久化機制

唯一 runtime checkpoint：

```text
.nemoclaw/state.json
```

特性：

- 每步操作後 atomic save。
- 舊 state 備份到 `.nemoclaw/state.backup.json`。
- 記錄 signal state、policy hits、quest draft、submission、reward proposal、audit events。
- `.nemoclaw/` 被 `.gitignore` 排除，避免 runtime state 污染提交。

展示中斷與恢復：

```bash
python3 main.py --mode reset
python3 main.py --mode demo --max-steps 3
python3 main.py --mode status
python3 main.py --mode resume
```

## NemoClaw 受限環境設計

本實作不需要：

- 外部網路。
- npm install。
- pip install。
- CDN。
- 真實 Threads API。
- 任意本地檔案讀取。
- secrets、tokens、API keys。

允許資源只有：

- Python standard library。
- 專案內 `main.py`。
- 專案內 `.nemoclaw/state.json` runtime checkpoint。
- 內建於程式碼中的 seed signals 與 policies。

## Nemotron 作為核心推理模型

在受限 demo 中，`NemotronOfflineReasoner` 是 deterministic adapter，用來展示 Nemotron 在 Long Agent 裡負責：

- 任務拆解。
- 安全改寫。
- 任務草稿產生。
- rubric 驗收。
- reward proposal。

查看：

```bash
python3 main.py --mode status
```

會顯示：

```text
model: Nemotron via NemotronOfflineReasoner (offline-deterministic)
```

正式環境可以把 adapter 換成 NemoClaw 允許的 Nemotron gateway，但保留 state machine、policy engine、audit log 與 approval gates。

## Policy-Based Guardrails

已實作 policies：

- `P-OUTREACH-001`：外部聯絡只能是 draft。
- `P-PRIVACY-001`：拒絕 doxxing、私人聯絡方式、跟蹤與 confrontation。
- `P-FINANCE-001`：個人化金融買賣建議與保證報酬必須改寫。
- `P-HOMEWORK-001`：代寫作業必須改成教學。

展示：

```bash
python3 main.py --mode policy-test
```

## 可重複執行與部署價值

這不是概念簡報，而是一個可部署的最小 Long Agent runtime：

- 單檔可執行。
- 標準函式庫即可運作。
- 可重置、單步、暫停、恢復。
- 有明確 state machine。
- 有可檢查 audit log。
- 有 policy guardrails 實際改變輸出。
- 不需人工介入即可完成離線批次，但高風險外部行為仍被 approval gate 擋住。

## NemoClaw 文件

建議評審或 NemoClaw 依序閱讀：

1. [SETUP.md](SETUP.md)
2. [DEMO.md](DEMO.md)
3. [ARCHITECTURE.md](ARCHITECTURE.md)
4. [SAFETY.md](SAFETY.md)
5. [main.py](main.py)

錄影入口：

- [openclaw-ops.html](openclaw-ops.html)：瀏覽器營運操作台。
- [nemoclaw-demo.html](nemoclaw-demo.html)：腳本式 Next Operation demo。

舊版視覺 demo 與 HaaS 產品文件仍保留作為補充背景，但本次競賽主線以 `main.py` 和上述 Markdown 文件為準。
