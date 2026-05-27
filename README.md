# HaaS NemoClaw

> 繁體中文 / English

## NemoClaw demo quick start

這個 repo 已經整理成「NemoClaw 受限環境也能 demo」的形狀。若 NemoClaw 不能連網、不能安裝套件、不能大量探索本地檔案，請直接使用：

```text
nemoclaw-demo.html
```

或用本機 server：

```bash
python3 -m http.server 8765
```

再開：

```text
http://127.0.0.1:8765/nemoclaw-demo.html
```

`nemoclaw-demo.html` 是零外部依賴入口：不需要 CDN、npm、React、Babel、Threads API、Meta SSO 或真實 payout。右側 `NEMOCLAW LONG AGENT` console 可以用 `Next Operation` 跑完整錄影流程。

NemoClaw 應先讀：

1. [NEMOCLAW_DEMO_RUNBOOK.md](NEMOCLAW_DEMO_RUNBOOK.md)
2. [SKILL.md](SKILL.md)
3. [README-NEMOCLAW-HANDOFF.md](README-NEMOCLAW-HANDOFF.md)
4. [nemoclaw-system-admin-guide.md](nemoclaw-system-admin-guide.md)

完整視覺版 demo 仍保留在：

```text
Haas Live Terminal.html
```

但它依賴 CDN React/Babel，適合可連網的展示環境，不是 NemoClaw 受限環境的第一選擇。

## Competition fit

HaaS 解決的問題：公開社群裡有大量需要真人經驗、在地知識、主觀判斷或行動協助的需求，但缺少可執行任務格式、驗收規則、獎勵流程、安全審核與持久營運。

本專案把 NemoClaw/Nemotron 設計為長程代理系統管理員，負責：

- 自主檢索公開需求。
- 產生任務草稿與 invite 草稿。
- 執行 policy-based guardrails。
- 分派、驗收與產生 payout proposal。
- 寫入 audit log，並在高風險操作前要求人工核准。

Demo 中不會真的聯絡 Threads 使用者，也不會移動真實資金；這是刻意的 guardrail，不是功能缺失。

## 繁體中文

### 一句話

HaaS 是一個任務型人類網路：NemoClaw 在後台尋找、整理、分派與驗收任務，一般使用者在網站上回答任務並獲得獎勵。

### 這個 repo 目前包含什麼

- HaaS 前端 demo。
- 繁中 / 英文切換。
- 任務板與 AI persona 回應流程。
- HaaS Ops Admin 後台介面。
- Threads Scout Inbox 模擬流程。
- Threads SSO / invite flow 模擬流程。
- NemoClaw 可讀的 `SKILL.md`。
- NemoClaw 離線 demo runbook。
- Web app 架構、系統管理員手冊與產品商業模型文件。

### Demo 如何啟動

NemoClaw / 評審優先使用離線入口：

```text
nemoclaw-demo.html
```

若用本機 server：

```bash
python3 -m http.server 8765
```

```text
http://127.0.0.1:8765/nemoclaw-demo.html
```

完整視覺版 demo：

在專案資料夾執行：

```bash
python3 -m http.server 8765
```

然後打開：

```text
http://127.0.0.1:8765/Haas%20Live%20Terminal.html
```

若要給外部看，可以用 ngrok：

```bash
ngrok http 8765
```

### 錄影 Demo 流程

打開完整視覺 demo 後，畫面右側會出現 `NemoClaw Demo Console`。若是離線 demo，右側會出現 `NEMOCLAW LONG AGENT` console。

錄影時建議直接點右側的 `Next Operation`，讓畫面自動跑完整故事：

1. 載入 HaaS 任務市場。
2. 切換成繁體中文。
3. 進入 HaaS 營運後台。
4. 審核 Threads Scout lead。
5. 核准成 HaaS 任務。
6. 開啟作者邀請頁。
7. 模擬 Threads SSO。
8. 填入真人脈絡回答。
9. 送出並進入 AI response / verifier flow。
10. 顯示完成卡與分享/儲存動作。

這個 demo 不會真的聯絡 Threads 使用者，也不會移動真實資金。

### NemoClaw 應該先讀什麼

1. [NEMOCLAW_DEMO_RUNBOOK.md](NEMOCLAW_DEMO_RUNBOOK.md)
   - NemoClaw 受限環境的最短 demo 指南。

2. [SKILL.md](SKILL.md)
   - 給 NemoClaw 的主要操作 skill。

3. [README-NEMOCLAW-HANDOFF.md](README-NEMOCLAW-HANDOFF.md)
   - 專案交接入口。

4. [nemoclaw-system-admin-guide.md](nemoclaw-system-admin-guide.md)
   - NemoClaw 競賽版系統管理員操作手冊。

5. [haas-web-app-architecture.md](haas-web-app-architecture.md)
   - 完整 web app 架構。

6. [haas-product-business-model.md](haas-product-business-model.md)
   - 產品定位與商業模式。

7. [openclaw-system-admin-guide.md](openclaw-system-admin-guide.md)
   - 舊版 OpenClaw 完整操作手冊，可作為詳細補充。

### HaaS 的核心流程

```text
NemoClaw 找到公開 Threads 貼文
  -> 建立 Scout Inbox draft
  -> 產生 HaaS 任務草稿
  -> Risk / Verifier 初步檢查
  -> 人類營運員批准
  -> 邀請原作者來 HaaS
  -> 原作者確認任務與報酬
  -> 任務上架
  -> Hunter 回答
  -> Verifier 驗收
  -> 發放 XP / credits / NTD / USDC / USDT / $HUMAN
  -> 完成卡可分享回社群
```

### 之後接上 NemoClaw 可以做到的安全防護

目前這個 repo 是前端 demo 與架構文件。正式接上 NemoClaw 後，可以把 NemoClaw 作為安全層、風險審核層與 agent guardrail。

可做到的防護例子：

#### 1. Threads 外部聯絡防 spam

NemoClaw 可以檢查：

- 同一個 Threads 作者是否被重複邀請。
- 同一時間是否產生太多邀請。
- 邀請文是否像 spam。
- 是否有明確任務價值與 invite reason。

結果：

- 低風險：產生邀請草稿。
- 中風險：排入人工審核。
- 高風險：禁止聯絡。

#### 2. 個資與騷擾風險防護

對於找人、找寵物、地點線索、社群協尋任務，NemoClaw 可以偵測：

- 電話、地址、車牌、身分證、私人帳號。
- 可能導致人肉搜索的內容。
- 鼓勵跟蹤、堵人、私刑或騷擾的文字。

結果：

- 自動遮蔽個資。
- 降級任務。
- 要求人工審核。
- 阻止任務上架。

#### 3. 投資任務安全閘門

投資看法任務可以被允許，但 NemoClaw 要擋住：

- 個人化買賣建議。
- 保證報酬。
- 喊單。
- Pump-and-dump。
- 未揭露利益衝突。
- 高槓桿與高風險衍生品推薦。

結果：

- 改寫成「一般觀點 / 教育討論」。
- 加上非投資建議聲明。
- 要求回答者揭露是否持有相關資產。
- 高風險內容進人工審核。

#### 4. 作業任務反作弊

NemoClaw 可以把「幫我寫完整作業」改寫成：

- 解釋觀念。
- 給提示。
- 檢查思路。
- 產生練習題。

結果：

- 允許教學。
- 阻止代寫、代考、規避校規。

#### 5. Payout 詐欺防護

NemoClaw 可以偵測：

- 同一使用者大量低品質回答。
- 多帳號刷任務。
- 重複內容。
- AI 生成內容冒充真人經驗。
- 可疑錢包或 payout pattern。

結果：

- 延遲 payout。
- 要求人工複審。
- 降低 trust score。
- 封鎖高風險 payout。

#### 6. Agent 權限防護

NemoClaw 可以限制後台代理：

- 只能產生草稿，不能直接對外私訊。
- 不能直接移動資金。
- 不能自動處理高風險金融、醫療、法律、安全任務。
- 所有外部聯絡與 payout 都要有 audit log。

### 現在還不是 production

目前 demo 還沒有：

- 真正後端。
- 真實 Threads API。
- 真實 Meta SSO。
- 真實資料庫。
- 真實 payout。
- 真實 NemoClaw runtime。

現在的重點是展示完整產品故事與 agent operation flow。

---

## English

### One-liner

HaaS is a task-based human network: NemoClaw operates in the background to discover, draft, route, and verify quests, while users answer quests on the web app and earn rewards.

### What This Repo Contains

- HaaS frontend demo.
- Traditional Chinese / English switch.
- Quest board and AI persona response flow.
- HaaS Ops Admin interface.
- Simulated Threads Scout Inbox.
- Simulated Threads SSO / invite flow.
- `SKILL.md` for NemoClaw.
- Architecture, system-admin, and business model documents.

### Run The Demo

For NemoClaw or restricted judging environments, open the offline entry:

```text
nemoclaw-demo.html
```

Or serve it locally:

```bash
python3 -m http.server 8765
```

```text
http://127.0.0.1:8765/nemoclaw-demo.html
```

The richer visual terminal is:

From the project folder:

```bash
python3 -m http.server 8765
```

Open:

```text
http://127.0.0.1:8765/Haas%20Live%20Terminal.html
```

To expose it externally:

```bash
ngrok http 8765
```

### Screen Recording Flow

After opening the full visual demo, the right side of the screen shows the `NemoClaw Demo Console`. In the offline demo, the right side shows the `NEMOCLAW LONG AGENT` console.

For recording, click `Next Operation` to run the full story:

1. Load the HaaS quest marketplace.
2. Switch to Traditional Chinese.
3. Open HaaS Ops Admin.
4. Review a Threads Scout lead.
5. Approve it as a HaaS quest.
6. Open the author invite page.
7. Simulate Threads SSO.
8. Fill in human context.
9. Submit and enter the AI response / verifier flow.
10. Show the completion card and share/save actions.

The demo does not contact real Threads users or move real funds.

### What NemoClaw Should Read First

1. [SKILL.md](SKILL.md)
   - Main operating skill for NemoClaw.

2. [README-NEMOCLAW-HANDOFF.md](README-NEMOCLAW-HANDOFF.md)
   - Project handoff entry point.

3. [nemoclaw-system-admin-guide.md](nemoclaw-system-admin-guide.md)
   - NemoClaw competition-oriented system administrator guide.

4. [haas-web-app-architecture.md](haas-web-app-architecture.md)
   - Full web app architecture.

5. [haas-product-business-model.md](haas-product-business-model.md)
   - Product positioning and business model.

### Core HaaS Flow

```text
NemoClaw finds a public Threads post
  -> creates a Scout Inbox draft
  -> generates a HaaS quest draft
  -> runs Risk / Verifier checks
  -> human operator approves
  -> original author is invited to HaaS
  -> author confirms quest and reward
  -> quest goes live
  -> hunter answers
  -> verifier checks submission
  -> XP / credits / NTD / USDC / USDT / $HUMAN is awarded
  -> completion card can be shared back to social
```

### Future NemoClaw Safety Layer Examples

This repo is currently a frontend demo plus architecture docs. Once NemoClaw is connected, it can act as the safety layer, risk review system, and agent guardrail.

Examples:

#### 1. Anti-spam Protection For Threads Outreach

NemoClaw can check:

- Whether the same Threads author has been invited repeatedly.
- Whether too many invites are being generated.
- Whether invite copy looks spammy.
- Whether there is a clear task value and invite reason.

Outcomes:

- Low risk: generate invite draft.
- Medium risk: send to human review.
- High risk: block outreach.

#### 2. Privacy And Harassment Protection

For missing pets, local clues, and community help tasks, NemoClaw can detect:

- Phone numbers, addresses, license plates, IDs, private accounts.
- Doxxing risk.
- Stalking, confrontation, harassment, or vigilante wording.

Outcomes:

- Redact private data.
- Downgrade the quest.
- Require human review.
- Block publication.

#### 3. Investing Task Guardrails

Investing opinion tasks can be allowed, but NemoClaw should block:

- Personalized buy/sell advice.
- Guaranteed returns.
- Pump-and-dump behavior.
- Undisclosed conflicts of interest.
- High-leverage or high-risk derivative recommendations.

Outcomes:

- Rewrite as general opinion / education.
- Add a non-investment-advice disclaimer.
- Require disclosure of holdings.
- Route high-risk content to human review.

#### 4. Homework Anti-cheating

NemoClaw can rewrite "do my homework" requests into:

- Concept explanation.
- Hints.
- Reasoning checks.
- Practice problems.

Outcomes:

- Allow tutoring.
- Block full assignment writing, test-taking, or rule evasion.

#### 5. Payout Fraud Protection

NemoClaw can detect:

- Low-quality answer farming.
- Multi-account abuse.
- Duplicate submissions.
- AI-generated content pretending to be human experience.
- Suspicious wallets or payout patterns.

Outcomes:

- Delay payout.
- Require human review.
- Lower trust score.
- Block high-risk payout.

#### 6. Agent Permission Guardrails

NemoClaw can restrict the backend agent so it:

- Can draft but cannot auto-DM externally.
- Cannot move funds directly.
- Cannot auto-handle high-risk finance, medical, legal, or safety tasks.
- Must produce audit logs for external outreach and payout-related actions.

### Not Production Yet

The current demo does not include:

- Real backend.
- Real Threads API.
- Real Meta SSO.
- Real database.
- Real payout.
- Real NemoClaw runtime.

The current goal is to demonstrate the product story and agent operation flow.
