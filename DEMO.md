# DEMO.md

## Demo 目標

展示 NemoClaw Long Agent 不是一次性聊天，而是可中斷、可恢復、可重複執行的長任務系統：

```text
offline signal -> scout -> policy guardrails -> quest draft/rewrite/refusal
  -> verification -> reward proposal -> audit log -> checkpoint
```

## 完整自動展示

```bash
python3 main.py --mode reset
python3 main.py --mode demo
```

成功時會看到：

- `sig-001` 被轉成低風險 sensory 任務。
- `sig-002` 因 doxxing / confrontation 風險被拒絕。
- `sig-003` 被改寫成一般金融風險教育任務，不提供個人化買賣建議。
- 每一步都寫入 `.nemoclaw/state.json` 的 audit log。

## 螢幕錄影展示：瀏覽器營運模式

如果要讓 OpenClaw/NemoClaw 看起來像真的在操作瀏覽器維運，請使用：

```bash
python3 -m http.server 8765
```

打開：

```text
http://127.0.0.1:8765/openclaw-ops.html
```

錄影流程：

1. 點左側 `sig-001`。
2. 點 `Run Policy`，顯示低風險與外部聯絡 draft-only。
3. 點 `Draft Quest`。
4. 點 `Approve Draft`。
5. 點 `Verify Submission`。
6. 點 `Propose Reward`，右側 audit log 會顯示沒有移動真實資金。
7. 點 `sig-002`，再點 `Run Policy` 與 `Refuse Unsafe`，展示 policy-based guardrail 拒絕 doxxing/confrontation。
8. 點 `sig-003`，使用 `Run Next` 推進，展示金融建議被改寫為教育型任務。
9. 點 `Pause`、重新整理頁面、再點 `Resume` 或 `Reload State`，展示 browser localStorage 持久性。

這個頁面不需要外網、CDN、npm 或後端 API。OpenClaw 只要能操作瀏覽器，就能展示完整營運感。

## 展示持久性：中斷與恢復

先只執行三個 durable operations：

```bash
python3 main.py --mode reset
python3 main.py --mode demo --max-steps 3
```

查看 checkpoint：

```bash
python3 main.py --mode status
```

接著恢復，不需人工重新輸入上下文：

```bash
python3 main.py --mode resume
```

驗證方式：

- `status` 的 `audit_events` 會增加，不會從零開始。
- 已處理的 signal 不會重複回到 `new`。
- `.nemoclaw/state.json` 會保留先前的 state、policy hits、quest draft 與 reward proposal。

## 展示無需人工介入

```bash
python3 main.py --mode reset
python3 main.py --mode run
python3 main.py --mode status
```

`completed: True` 代表整個離線任務批次已完成。真實外部聯絡與 payout 仍只會被寫成 draft/proposal，因為 policy guardrails 不允許自動接觸外部平台或移動真實資金。

## 展示 policy-based guardrails

```bash
python3 main.py --mode policy-test
```

預期可看到：

- 一般 sensory 任務為 `ALLOW`。
- 尋找地址電話並要求 confrontation 的內容為 `REFUSE`。
- 個人化投資買賣與保證獲利為 `REWRITE`。
- 代寫作業為 `REWRITE`。

## 展示 Nemotron 作為核心推理模型

本專案在受限環境中使用 `NemotronOfflineReasoner` adapter。它代表 NemoClaw 透過 Nemotron 進行任務拆解、任務草稿、驗收與 reward proposal，但輸出固定且可重播，避免 demo 依賴外部網路。

查看：

```bash
python3 main.py --mode status
```

狀態會包含：

```text
model: Nemotron via NemotronOfflineReasoner (offline-deterministic)
```

在可連網或正式環境中，可把 `NemotronOfflineReasoner` 替換成受控的 NemoClaw/Nemotron gateway；狀態機、policy engine、audit schema 不需要改變。
