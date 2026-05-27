# HaaS / OpenClaw Handoff

這個資料夾目前包含 HaaS 的 demo 前端、商業模型與 OpenClaw 交接文件。

## 你應該先讀

0. [SKILL.md](SKILL.md)
   - 可直接交給 OpenClaw 的 skill 版本，包含它作為 HaaS 系統管理員的核心規則、流程與邊界。

1. [haas-product-business-model.md](haas-product-business-model.md)
   - 產品定位、商業模式、MVP demo、原始資料模型。

2. [haas-web-app-architecture.md](haas-web-app-architecture.md)
   - 完整 Web App 架構、服務切分、資料模型、API、支付與風險設計。

3. [openclaw-system-admin-guide.md](openclaw-system-admin-guide.md)
   - 給 OpenClaw 的系統管理員操作手冊，說明它可以做什麼、不能做什麼、什麼需要人工審核。

## Demo 前端

開啟：

```text
Haas Live Terminal.html
```

目前 demo 已包含：

- HaaS 任務板。
- 繁中 / 英文切換。
- HaaS Ops Admin。
- Threads Scout Inbox。
- Threads SSO 模擬流程。
- 回答任務。
- AI streaming 回應。
- 分享與下載完成卡。

## OpenClaw 在正式系統中的位置

```text
HaaS Web App
  -> HaaS Backend
  -> Internal OpenClaw Gateway
  -> OpenClaw Agent Runtime
  -> Audit Logs / Database / Queue
```

OpenClaw 不應直接操作前端，也不應直接移動資金。它應該透過 internal API 建立任務草稿、審核建議、風險標記與營運待辦。
