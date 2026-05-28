# HaaS / NemoClaw + OpenClaw Handoff

這個資料夾目前包含 HaaS 的 demo 前端、NemoClaw 離線入口、商業模型與 agent handoff 文件。

競賽提交時，請把 NemoClaw 視為主要安全與長程代理展示層，把 OpenClaw 視為可替換的 agent framework / operator 名稱。核心概念是同一個：後台 agent 不只是聊天，而是持久執行 scout、draft、policy review、verification、payout proposal 與 audit logging。

## 你應該先讀

0. [NEMOCLAW_DEMO_RUNBOOK.md](NEMOCLAW_DEMO_RUNBOOK.md)
   - NemoClaw 受限環境的最短 demo 指南。若只能讀少量檔案，先讀這份。

1. [SKILL.md](SKILL.md)
   - 可直接交給 NemoClaw/OpenClaw 的 skill 版本，包含它作為 HaaS 系統管理員的核心規則、流程與邊界。

2. [haas-product-business-model.md](haas-product-business-model.md)
   - 產品定位、商業模式、MVP demo、原始資料模型。

3. [haas-web-app-architecture.md](haas-web-app-architecture.md)
   - 完整 Web App 架構、服務切分、資料模型、API、支付與風險設計。

4. [openclaw-system-admin-guide.md](openclaw-system-admin-guide.md)
   - 給後台 agent 的系統管理員操作手冊，說明它可以做什麼、不能做什麼、什麼需要人工審核。

## NemoClaw 離線 Demo

優先開啟：

```text
nemoclaw-demo.html
```

這是競賽/評審環境的首選入口，因為它不依賴網路、CDN、npm、React、Babel 或任何真實外部 API。

用本機 server：

```bash
python3 -m http.server 8765
```

```text
http://127.0.0.1:8765/nemoclaw-demo.html
```

打開後按右側 NemoClaw console 的 `Next Operation`，即可展示完整流程：

```text
scout -> policy guardrails -> quest draft -> approval -> invite -> SSO simulation -> human answer -> verification -> completion card
```

## 完整視覺 Demo 前端

開啟：

```text
Haas Live Terminal.html
```

這份 demo 較漂亮，但依賴 CDN React/Babel。若 NemoClaw 或評審環境不能連網，請改用 `nemoclaw-demo.html`。

目前完整視覺 demo 已包含：

- HaaS 任務板。
- 繁中 / 英文切換。
- HaaS Ops Admin。
- Threads Scout Inbox。
- Threads SSO 模擬流程。
- 回答任務。
- AI streaming 回應。
- 分享與下載完成卡。

## NemoClaw 在正式系統中的位置

```text
HaaS Web App
  -> HaaS Backend
  -> Internal NemoClaw Gateway
  -> Nemotron reasoning model
  -> NemoClaw policy engine
  -> Audit Logs / Database / Queue
  -> Human approval console
```

NemoClaw 不應直接操作外部平台，也不應直接移動資金。它應該透過 internal API 建立任務草稿、審核建議、風險標記、驗收結果、payout proposal 與營運待辦。所有外部聯絡與真實 payout 都要經過 policy gate、audit log 與人工或 requester approval。
