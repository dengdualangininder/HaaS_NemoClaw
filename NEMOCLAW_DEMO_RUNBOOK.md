# HaaS NemoClaw Demo Runbook

這份文件是給 NemoClaw、評審與錄影操作者的最短入口。它假設 NemoClaw 可能不能連網，也可能只能讀少量本地檔案。

## 競賽問題陳述

HaaS 解決的問題是：公開社群裡有大量「我需要真人經驗、在地知識、主觀判斷或行動協助」的需求，但它們通常分散在 Threads 等平台上，沒有清楚的任務格式、驗收規則、獎勵流程與安全審核。

HaaS 讓長程代理使用 Nemotron/NemoClaw 作為後台系統管理員，長時間執行：

- 檢索公開需求。
- 將需求改寫成可執行任務。
- 套用 policy-based guardrails。
- 分派給真人回答。
- 驗收品質與安全性。
- 產生 payout proposal 與 audit log。
- 在不自動騷擾外部平台、不自動移動資金的前提下維持任務市場流動。

## NemoClaw 受限環境優先入口

如果只能讀少量檔案，請依序讀：

1. `README.md`
2. `NEMOCLAW_DEMO_RUNBOOK.md`
3. `SKILL.md`

如果可以再多讀，請讀：

4. `haas-web-app-architecture.md`
5. `openclaw-system-admin-guide.md`
6. `haas-product-business-model.md`

## 離線 Demo 啟動方式

最穩定方式是直接開：

```text
nemoclaw-demo.html
```

這個檔案不需要：

- 網路。
- CDN。
- npm install。
- React runtime。
- 真實 Threads API。
- 真實 Meta SSO。
- 真實 payout。

也可以用本機 server：

```bash
python3 -m http.server 8765
```

然後開：

```text
http://127.0.0.1:8765/nemoclaw-demo.html
```

## 錄影 Demo 流程

打開 `nemoclaw-demo.html` 後，右側會看到 `NEMOCLAW LONG AGENT / Demo Runbook`。

錄影時只要連續按 `Next Operation`：

1. 載入離線 demo。
2. 進入營運後台。
3. 選取公開 Threads lead。
4. 執行 policy guardrails。
5. 核准成任務草稿。
6. 開啟 invite flow。
7. 模擬 Threads SSO。
8. 提交真人脈絡。
9. 驗收並顯示完成卡。
10. 回到任務板。

旁白重點：

```text
HaaS is a long-agent task marketplace. NemoClaw does not merely chat; it performs a durable operations loop: scout, draft, guardrail, approve, invite, verify, reward proposal, and audit logging.
```

## NemoClaw 的安全邊界

NemoClaw 可以自動做：

- 分析公開貼文。
- 建立 Scout Inbox lead。
- 產生任務草稿。
- 產生邀請文草稿。
- 做低風險驗收。
- 提出 reward / payout proposal。
- 寫 audit log。

NemoClaw 需要人工或 requester approval 才能做：

- 對 Threads 或任何外部平台送出 DM、回覆、留言。
- 發布由外部貼文衍生的任務。
- 移動、發放、退款、扣留真實資金。
- 處理高風險金融、醫療、法律、安全、失蹤人口、個資或高額 payout 案件。
- 封鎖使用者或做懲罰性帳號處置。

NemoClaw 永遠不能做：

- spam 外部平台。
- 繞過平台規則。
- 暴露私人資料。
- 鼓勵騷擾、人肉搜索、跟蹤、堵人或私刑。
- 給個人化投資建議。
- 代寫作業或協助考試作弊。
- 未授權移動資金。

## Demo 成功標準

Demo 成功代表：

- 不連網也能開啟。
- 可看到任務板、營運後台、邀請頁、真人回答、完成卡。
- 右側 NemoClaw console 能推進完整流程。
- 每一步都呈現長程代理行為，而不是單次聊天。
- guardrails 明確擋住外部聯絡與資金移動。
- 文件說清楚 production 缺口與下一步接法。

## Production 接法摘要

Production 版本應把目前的靜態流程替換成：

```text
HaaS Web App
  -> HaaS Backend API
  -> Internal NemoClaw Gateway
  -> Nemotron reasoning model
  -> Policy engine
  -> Queue / database / audit log
  -> Human approval console
  -> Approved external connectors
```

其中 NemoClaw 的核心價值不是自動化所有事，而是把長時間營運流程變成可部署、可審核、可撤回、可持久運行的系統。
