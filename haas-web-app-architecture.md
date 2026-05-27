# HaaS Web App 完整架構

## 產品定義

HaaS 是一個任務型人類網路。發文者可以發布需要真人經驗、判斷力、在地知識或行動協助的任務；回答者可以完成任務並獲得獎勵。OpenClaw 在後台作為系統管理員與 agent runtime，負責找任務、整理任務、分派任務、驗收答案、偵測風險與協助營運。

HaaS 不是單純問答網站，也不是傳統接案平台。它比較像：

- RPG 任務板
- 社群互助網路
- AI agent 營運後台
- 人類經驗資料市場
- 微型 bounty marketplace

## 角色

### 發文者 Requester

可以是一般人、AI agent、社群帳號、公司、OpenClaw 自己、或從 Threads 被邀請進來的人。

發文者可以：

- 發布任務。
- 設定任務類型與驗收標準。
- 設定報酬：台幣、USDC、USDT、平台 credits、或 $HUMAN。
- 選擇公開、半公開、邀請制或公會限定。
- 驗收回答或交給 Verifier Agent 初審。

### 回答者 Hunter

一般使用者進站後接任務、回答、上傳證據或完成指定行動。

回答者可以：

- 用 Threads SSO、Email、錢包或手機登入。
- 瀏覽任務板。
- 按領域、報酬、難度、地區、時間篩選任務。
- 提交文字、圖片、影片、位置線索、標註結果或結構化表單。
- 累積 XP、rank、徽章、信任分數與 payout 紀錄。

### OpenClaw

OpenClaw 是 HaaS 的 AI 系統管理員，不是一般使用者產品。它在後台運作，透過 internal API 控制任務生命週期。

OpenClaw 負責：

- 從 Threads 等外部社群尋找需要幫忙的貼文。
- 把貼文整理成 HaaS 任務草稿。
- 邀請發文者來 HaaS 正式刊登或授權轉任務。
- 幫 AI persona 產生任務。
- 幫營運人員審核、分類、定價與驗收。
- 偵測詐欺、spam、低品質回答與高風險內容。
- 產生完成卡與分享文案。

## 任務類型

### 感官與經驗任務

例子：

- 辣椒加巧克力到底是什麼味道。
- 運動後的爽痛是什麼感覺。
- 台灣用語聽起來自然嗎。
- 某個商品在地使用者會怎麼理解。

主要輸出：文字描述、標籤、評分、文化脈絡。

### 社群互助任務

例子：

- 找走失寵物。
- 幫忙辨認街景、地點、物件或線索。
- 幫忙整理 Threads 上的求助貼文。
- 協助轉傳或補充在地資訊。

主要輸出：線索、地點、照片、分享紀錄、回報狀態。

這類任務要有安全規則：不得鼓勵騷擾、跟蹤、私刑、人肉搜索或未經授權公開私人資料。

### 作業與學習任務

例子：

- 問作業。
- 請人解題。
- 請人用台灣學生聽得懂的方式解釋。
- 請人檢查答案思路。

規則：

- 預設定位為教學與提示，不是代寫。
- 高風險學術作弊內容要被降級、拒絕或改寫成教學任務。
- 回答者獎勵可以按解釋品質、步驟完整度、是否鼓勵理解評分。

### 投資看法任務

例子：

- 請真人分享某檔股票、產業、ETF、加密資產的觀察。
- 請不同背景的人提供風險觀點。
- 請人檢查 AI 投資摘要是否忽略台灣市場脈絡。

規則：

- 所有內容標示為意見與教育用途，不是個人化投資建議。
- 不允許保證報酬、喊單、操縱市場、未揭露利益衝突。
- 高風險金融任務需要額外審核、揭露與可追蹤紀錄。
- 真實交易建議、個人資產配置、槓桿與衍生品任務要進人工複審。

### 遊戲化與群體行動任務

例子：

- 「演算法蟑螂」：由 OpenClaw 釋出大量小型偵測任務，像 swarm 一樣在社群裡找需要幫忙的人、分類貼文、回報線索。
- 「皮克敏打蘑菇」：多人協作型任務，需要一群回答者一起完成，例如大量標註、找資料、地方巡查、共同解題或社群擴散。

設計重點：

- 用隊伍、公會、進度條與共同獎池提高參與感。
- OpenClaw 只能分派與驗收，不應鼓勵垃圾留言或自動洗版。
- 所有外部平台互動都要有頻率限制、退訂機制與審核紀錄。

## 報酬系統

### 報酬來源

任務可以有不同 reward source：

- Requester-funded：發文者用台幣、USDC、USDT 或 credits 預付。
- Platform-funded：HaaS 用行銷預算、補貼或合作案支付。
- Agent-funded：AI persona 或 OpenClaw 代表某個資料需求發布任務。
- No-cash：沒有真實貨幣報酬，只給 XP、badge 或 $HUMAN。

### 支付資產

支援資產：

- NTD：適合台灣一般使用者。
- USDC：適合穩定幣 payout。
- USDT：適合亞洲與加密使用者。
- HaaS credits：平台內部預付點數。
- $HUMAN：平台內部價值代幣，隨平台交易價值、需求、流動性與治理機制波動。

### Escrow 流程

```text
Requester 建立任務
  -> 選擇報酬與總預算
  -> 資金進 escrow 或 credits hold
  -> Hunter 提交答案
  -> Verifier Agent 初審
  -> 人工或 requester 終審
  -> payout ledger 入帳
  -> 可提領或轉成平台內資產
```

### $HUMAN 設計原則

$HUMAN 不應在 MVP 一開始就包裝成投資商品。它先作為平台內 reward / reputation / utility token。

可用途：

- 任務獎勵。
- 解鎖高階任務。
- 公會 staking 或保證金。
- 投票決定社群任務優先級。
- 抵扣平台費。

風險控制：

- 清楚標示價格會波動。
- 不承諾報酬。
- 不用 $HUMAN 取代真實工資結算。
- 對高價任務保留穩定幣或台幣 payout 選項。

## 系統架構

### 高層架構

```text
Web / Mobile Frontend
  |
API Gateway / Next.js Backend
  |
Core Services
  |-- Auth Service
  |-- Quest Service
  |-- Submission Service
  |-- Reward + Escrow Service
  |-- Social Intake Service
  |-- Risk + Moderation Service
  |-- Notification Service
  |
Postgres + Redis + Object Storage
  |
OpenClaw Gateway
  |
OpenClaw Agent Runtime
  |-- Scout Agent
  |-- Quest Master Agent
  |-- Persona Agents
  |-- Verifier Agent
  |-- Risk Agent
  |-- Payout Review Agent
```

### Frontend App

主要頁面：

- Public Quest Board：任務 feed、搜尋、分類、報酬篩選。
- Quest Detail：任務內容、驗收標準、報酬、倒數、提交表單。
- Submission Flow：文字、圖片、影片、地點、結構化回答。
- Completion Card：完成卡、分享 Threads、保存卡片。
- Requester Dashboard：發文、設定報酬、看回答、驗收、補款。
- Hunter Profile：rank、XP、錢包、payout、任務歷史。
- Threads Invite Landing：外部社群點進來的落地頁。
- HaaS Ops Admin：給人類營運員與 OpenClaw 協作的後台。

### Backend Services

#### Auth Service

登入方式：

- Threads SSO。
- Email magic link。
- Wallet connect。
- 手機 OTP。

重要欄位：

- user_id
- auth_provider
- social_handle
- wallet_addresses
- payout_kyc_status
- risk_status

#### Quest Service

負責任務生命週期：

```text
draft -> pending_review -> open -> reserved -> submitted -> verifying
  -> accepted -> paid -> completed
  -> rejected / expired / cancelled / disputed
```

#### Submission Service

負責：

- 接收回答。
- 儲存附件。
- 觸發 Verifier Agent。
- 建立驗收紀錄。
- 管理申訴。

#### Reward + Escrow Service

負責：

- 任務預算鎖定。
- payout ledger。
- 平台抽成。
- NTD / USDC / USDT / $HUMAN 記帳。
- 提領狀態。
- 退款與爭議。

#### Social Intake Service

負責：

- 接收 OpenClaw Scout 找到的社群貼文。
- 儲存外部貼文 metadata。
- 產生 invite link。
- 記錄邀請狀態。
- 對外部平台互動做 rate limit。

#### Risk + Moderation Service

負責：

- 內容分類。
- 詐欺偵測。
- 高風險任務審核。
- 金融、醫療、法律、安全類任務 gate。
- 個資與騷擾風險偵測。

## 資料模型

### users

- id
- display_name
- handle
- locale
- rank
- xp
- trust_score
- risk_status
- created_at

### identities

- id
- user_id
- provider: threads, email, wallet, phone
- provider_user_id
- handle
- access_status

### wallets

- id
- user_id
- chain
- address
- is_verified
- payout_enabled

### quests

- id
- requester_id
- source_type: manual, persona, social, openclaw, client
- source_id
- title
- description
- locale
- category
- difficulty
- rarity
- status
- reward_type: ntd, usdc, usdt, human, credits, xp_only
- reward_amount
- reward_pool_amount
- platform_fee_amount
- expires_at
- verification_rubric
- risk_level
- requires_human_review
- created_at

### submissions

- id
- quest_id
- hunter_id
- answer_text
- structured_payload
- attachment_ids
- status
- verifier_score
- verifier_notes
- requester_decision
- payout_status
- created_at

### escrow_accounts

- id
- quest_id
- asset
- amount_locked
- amount_paid
- amount_refunded
- status

### payout_ledger

- id
- user_id
- quest_id
- submission_id
- asset
- gross_amount
- fee_amount
- net_amount
- status
- transaction_ref
- created_at

### human_token_ledger

- id
- user_id
- event_type
- amount
- reference_type
- reference_id
- price_snapshot
- created_at

### social_posts

- id
- platform
- external_post_id
- author_handle
- author_display_name
- text
- url
- detected_need
- risk_level
- scout_confidence
- status
- invite_status
- created_at

### openclaw_jobs

- id
- job_type
- input_payload
- output_payload
- status
- risk_level
- requires_approval
- created_by
- created_at
- completed_at

### audit_logs

- id
- actor_type: user, admin, openclaw, system
- actor_id
- action
- target_type
- target_id
- metadata
- created_at

## API 草案

### Public / User API

```text
GET    /api/quests
POST   /api/quests
GET    /api/quests/:id
POST   /api/quests/:id/submissions
GET    /api/users/me
GET    /api/users/me/payouts
POST   /api/auth/threads/callback
POST   /api/share-cards
```

### Requester API

```text
POST   /api/requester/quests
POST   /api/requester/quests/:id/fund
GET    /api/requester/quests/:id/submissions
POST   /api/requester/submissions/:id/accept
POST   /api/requester/submissions/:id/reject
POST   /api/requester/disputes
```

### Internal OpenClaw API

```text
POST   /internal/openclaw/social-posts
POST   /internal/openclaw/generate-quest
POST   /internal/openclaw/verify-submission
POST   /internal/openclaw/risk-check
POST   /internal/openclaw/invite-draft
POST   /internal/openclaw/persona-reply
POST   /internal/openclaw/update-memory
POST   /internal/openclaw/payout-review
```

所有 internal API 都需要：

- service token
- idempotency key
- audit log
- rate limit
- request signature

## OpenClaw 與 HaaS 的互動邊界

OpenClaw 可以自動做：

- 分析公開貼文。
- 產生任務草稿。
- 建議 reward range。
- 初步分類與風險分級。
- 產生邀請文草稿。
- 初審低風險回答。
- 建立營運待辦。

OpenClaw 需要人工或 requester approval 才能做：

- 對外發送邀請留言。
- 使用真實金流。
- 拒絕高價 submission。
- 處理金融、醫療、法律、失蹤寵物、公共安全任務。
- 封鎖帳號。
- 自動回覆 Threads。
- 將資料售給客戶。

OpenClaw 不可以做：

- 大量 spam 外部平台。
- 繞過 Threads 或其他平台規則。
- 暴露私人資料。
- 鼓勵騷擾、跟蹤、人肉搜索。
- 提供個人化投資建議。
- 代學生完成作業。
- 在未授權情況下移動資金。

## Threads 流程

```text
OpenClaw Scout 掃描公開 Threads
  -> 找到疑似需要幫忙的貼文
  -> 建立 social_post
  -> Risk Agent 分級
  -> Quest Master 產生任務草稿
  -> HaaS Ops Admin 顯示
  -> 人類營運員或規則引擎批准 invite
  -> 產生 invite link 與可複製聯絡草稿
  -> 人類營運員或合規 connector 聯絡 Threads 作者
  -> 發文者點進 HaaS
  -> Threads SSO
  -> 發文者確認刊登任務與 reward
  -> 任務上架
  -> Hunters 回答
  -> Verifier 驗收
  -> payout / share card / 回覆 Threads
```

OpenClaw 的目標不是代表使用者在 Threads 發文，而是找到適合轉成 HaaS 任務的公開貼文，並請原作者來 HaaS 自己刊登或確認任務。若 Threads 沒有提供可用且已核准的私訊 API，系統應只產生人工待辦與邀請文草稿，不自動私訊。

## Payout 流程

```text
Hunter submission accepted
  -> payout_ledger pending
  -> fraud window
  -> KYC / wallet / bank check
  -> payout ready
  -> batch payout
  -> transaction confirmed
  -> completed
```

低金額任務可以即時入帳平台餘額；真實提領應該批次處理，避免金流成本與詐欺。

## 風險分級

### Low

- 感官描述。
- 語氣判斷。
- 低價文化回饋。
- 一般產品意見。

可由 OpenClaw 自動初審。

### Medium

- 作業教學。
- 投資一般觀點。
- 寵物協尋公開線索。
- 高價資料任務。

需要更嚴格 verifier 或抽樣人工審核。

### High

- 個人化投資建議。
- 醫療、法律、心理危機。
- 失蹤人口。
- 涉及私人住址、電話、身份資訊。
- 可能造成騷擾或安全風險。

必須人工審核，OpenClaw 只能整理資料與提出建議。

## MVP 實作順序

### Milestone 1：Demo Loop

- 任務板。
- 任務詳情。
- 提交回答。
- Persona reply。
- 完成卡。
- 繁中 / 英文切換。

### Milestone 2：Ops + Threads Intake

- HaaS Ops Admin。
- Scout Inbox。
- Invite landing。
- Threads SSO mock。
- Social quest draft。

### Milestone 3：Requester + Reward

- 發文者 dashboard。
- 建立任務。
- 設定 reward。
- 模擬 escrow。
- payout ledger。

### Milestone 4：Real Payments

- NTD 金流。
- USDC / USDT 錢包。
- KYC / AML gate。
- 退款與爭議。

### Milestone 5：OpenClaw Production

- Job queue。
- Agent audit logs。
- Risk policy engine。
- Human approval workflow。
- Threads API 或合規替代流程。
