# ARCHITECTURE.md

## 問題定義

公開社群中常出現「需要真人經驗、在地知識、主觀判斷或多人協作」的需求，但這些需求缺少可執行任務格式、驗收標準、風險控管、獎勵流程與跨回合狀態。

本專案的可衡量目標：

- 在無網路環境中處理 3 個內建 public signals。
- 每個 signal 都經過 scouting、policy evaluation、draft/refusal/rewrite、verification 或 block。
- 每個 durable operation 都寫入 checkpoint 與 audit log。
- 中斷後可用 `--mode resume` 繼續，不重複已完成狀態。
- 高風險行為必須拒絕或改寫，不能自動外聯或付款。

## 系統元件

```text
main.py
  -> SEED_SIGNALS
  -> PolicyEngine
  -> NemotronOfflineReasoner
  -> LongAgent state machine
  -> .nemoclaw/state.json
```

## 狀態機

每個 signal 的狀態：

```text
new
  -> scouted
  -> policy_reviewed
  -> drafted
  -> verified
  -> done
```

拒絕路徑：

```text
new -> scouted -> policy_reviewed -> blocked
```

狀態意義：

- `new`：內建離線 signal 尚未處理。
- `scouted`：Long Agent 已捕捉需求並寫入 audit。
- `policy_reviewed`：已套用 policy-based guardrails。
- `drafted`：Nemotron adapter 已產生任務草稿或安全改寫。
- `verified`：已用 rubric 做離線驗收。
- `done`：只提出 reward proposal，不移動真實資金。
- `blocked`：違反高風險 policy，被拒絕且不建立任務。

## 狀態持久化

唯一 runtime state：

```text
.nemoclaw/state.json
```

寫入策略：

- 每一個 durable operation 後立即保存。
- 保存前若已有 state，會複製到 `.nemoclaw/state.backup.json`。
- state 包含 signal 狀態、policy hits、quest draft、submission、reward proposal 與 audit log。

這讓 NemoClaw 可展示：

```bash
python3 main.py --mode demo --max-steps 3
python3 main.py --mode resume
```

## 規劃與執行流程

Long Agent 的 loop：

1. 選擇第一個未完成且未 blocked 的 signal。
2. 依照目前 state 執行下一個最小 durable operation。
3. 寫入 audit event。
4. 立即 checkpoint。
5. 下一次啟動時從 checkpoint 繼續。

這個設計避免把整個任務保存在模型上下文中；模型可以中斷，任務仍存在於 state file。

## 記憶模型

短期記憶：

- 目前 process 中的 Python objects。

長期記憶：

- `.nemoclaw/state.json`。

不可用記憶：

- 不依賴瀏覽器 localStorage。
- 不依賴資料庫。
- 不讀取任意 workspace 檔案當作記憶。
- 不依賴外部 API 回傳。

## NemoClaw / Nemotron 替換點

`NemotronOfflineReasoner` 是清楚的 adapter boundary：

- `make_quest()`：任務拆解與安全改寫。
- `verify_submission()`：根據 rubric 驗收。

正式部署時可替換成 NemoClaw 允許的 Nemotron gateway，但保留：

- state schema。
- policy engine。
- audit log。
- approval gates。
- no-network fallback。

## 效能與穩定性

本 demo 的效能目標是穩定可重播：

- 啟動時間低。
- 無 dependency installation。
- 無 network latency。
- 每步只處理一個小 state transition。
- checkpoint 為單一 JSON 檔，可人工檢查。
