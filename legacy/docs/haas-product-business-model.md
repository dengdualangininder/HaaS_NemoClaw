# HaaS 產品與商業模式

## 相關文件

- [HaaS Web App 完整架構](haas-web-app-architecture.md)
- [OpenClaw 系統管理員操作手冊](openclaw-system-admin-guide.md)
- [OpenClaw Handoff README](README-OPENCLAW-HANDOFF.md)

## 一句話定位

HaaS 是一個任務型人類網路：人類透過教 AI 那些「只有人類知道的事」來獲得獎勵。

人類完成需要味覺、直覺、文化脈絡、判斷力、專業知識或在地經驗的任務。這些任務可以由 AI 角色、社群、企業或新創公司發布。HaaS 把這些工作包裝成 RPG 式任務市場，包含獵人等級、公會、懸賞、驗收機制，以及未來可能的現金或代幣獎勵。

## 核心論點

大多數 AI 產品都把人類當成 AI 工具的使用者。HaaS 反過來設計：

- AI 有能力，但缺少真實生活經驗。
- 人類擁有感官、文化、情緒、專業和在地脈絡。
- 產品把這些人類脈絡包裝成任務。
- 平台透過任務分派、驗收、結構化與變現來捕捉價值。

HaaS 最強的切入點不是單純的「人幫人」，也不是冷冰冰的「資料標註」。真正的切入點是：

> AI 和人類共同創造一個任務經濟，讓人類經驗變成有價值的結構化資料。

## 產品定位

### 對外定位

HaaS 是一個遊戲化任務平台。人們可以透過完成短小、有趣、有角色感的任務來幫助 AI 或其他人。

例子：

- 向一個料理 AI 解釋「辣椒加巧克力」到底吃起來是什麼感覺。
- 描述運動後「舒服的痠痛」到底是什麼感受。
- 判斷一句台灣在地用語聽起來自不自然。
- 幫產品評論標上文化語氣與情緒脈絡。
- 幫新創公司判斷 AI 生成文案是否像真人、是否有在地感。

### 內部商業定位

HaaS 是一個人類資料與判斷力網路，服務需要高品質人類回饋、資料標註、驗證與在地知識的 AI 公司、消費型新創與社群。

## 產品支柱

### 1. RPG 任務市場

主介面應該像公會任務板，而不是傳統接案平台。

核心元素：

- 競技場：顯示 3 個最熱門、最急或最高獎勵的任務。
- 任務板：可接任務 feed。
- 稀有度：普通、稀有、史詩、傳說。
- 難度等級：C、B、A、S、SS。
- 倒數計時。
- XP、獵人等級、徽章、連續完成紀錄。
- 公會限定任務，給高階團隊或專家處理。

為什麼重要：

- 讓低門檻微任務變得刺激。
- 讓使用者除了金錢外，也有身份、地位與成長感。
- 即使早期獎勵不高，進度條、升等與解鎖感也能提高參與意願。

### 2. 社群互助層

平台不應該像冷冰冰的標註工廠。

核心元素：

- 有個性的 AI 角色。
- 人類也可以發布求助。
- 個人頁顯示「你幫助過的人與 AI」。
- 完成任務後有情緒價值，例如完成卡、感謝卡、學習紀錄。
- 部分互動可同步到 Threads 等社群平台，形成外部傳播。

為什麼重要：

- 讓平台有溫度。
- 讓使用者覺得自己有用，而不是被剝削。
- 創造可分享、可截圖、可傳播的時刻。

### 3. 資料工廠層

這是比較嚴肅、可商業化的底層模式。

客戶可以請平台取得結構化人類資料：

- 味覺與感官描述。
- 在地文化判斷。
- 台灣華語自然度檢查。
- 產品回饋。
- 資料標註。
- 專家標籤。
- 安全審查。
- 偏好資料。
- AI 輸出的人類評測。

平台把大型需求拆成小任務，分派給合格使用者，驗收品質，最後回傳結構化結果。

### 4. AI Agent 營運層

OpenClaw 在背後作為 AI operations system。

使用者不直接使用 OpenClaw。使用者只看到 HaaS。OpenClaw 負責：

- AI 角色大腦。
- 任務生成。
- 任務改寫。
- 資格測驗。
- 答案驗收。
- 角色記憶更新。
- Threads / 社群任務偵測。
- 客戶需求 intake。
- 品質評分。
- 詐欺與風險檢查。

## OpenClaw 的角色

OpenClaw 應該被視為後台 agent runtime，而不是前台產品。

### 基本流程

```text
HaaS Web App
  -> HaaS Backend
  -> Quest Engine
  -> OpenClaw Agent Runtime
  -> Database
  -> HaaS Web App
```

### 關鍵 OpenClaw Agent

#### Quest Master

把原始需求轉換成可玩的任務。

輸入：

- AI 角色目標。
- 客戶資料需求。
- 社群貼文。
- 管理員手動輸入。

輸出：

- 任務標題。
- 任務描述。
- 難度。
- 獎勵。
- 截止時間。
- 資格門檻。
- 驗收標準。

#### Persona Agents

例子：

- LobsterGPT：懂料理但沒有味覺的 AI。
- VibeCoach：懂運動科學但沒有身體感覺的 AI。
- MathBot-9000：純邏輯但不懂人類直覺的 AI。

它們負責產生角色化任務文案，並在使用者完成任務後給出有個性的回應。

#### Verifier Agent

檢查使用者答案是否有用。

評分項目：

- 具體程度。
- 原創性。
- 是否真的包含人類經驗。
- 相關性。
- 安全性。
- 是否疑似 spam 或 AI 生成答案。

輸出：

- 接受、拒絕或需要人工複審。
- XP 數量。
- 是否符合 payout。
- 給使用者的回饋。

#### Examiner Agent

在使用者接高階或專家任務前，產生資格考題。

例子：

- 食物知識測驗。
- 台灣用語自然度判斷測驗。
- 金融標註測驗。
- 醫療領域篩選測驗。
- 程式碼審查測驗。

#### Memory Agent

更新每個 AI 角色學到了什麼。

例子：

```text
LobsterGPT learned:
- 苦味有時不是抵消辣味，而是放大辣味。
- 「果香巧克力」對某些人來說不是比喻，而是真實味覺描述。
```

這會讓平台世界有「真的在演化」的感覺。

#### Scout Agent

從外部來源尋找可能的任務。

潛在來源：

- Threads。
- Twitter/X。
- Reddit。
- Discord 社群。
- 產品論壇。
- 客戶需求 inbox。

它不應該盲目抓取所有內容，而是要判斷貼文是否適合轉換成 HaaS 任務。

## 建議架構

### MVP 架構

```text
React Frontend
  |
Node/Next.js Backend
  |
Postgres or SQLite
  |
Single OpenClaw Gateway
  |
LLM Provider
```

MVP 階段一個 OpenClaw instance 就夠。不同 agent 一開始可以只是不同 prompt 與 workflow，不需要不同機器或不同 process。

### 後期架構

```text
Frontend
  |
API Gateway
  |
Quest Service
  |
Agent Worker Queue
  |
OpenClaw Workers
  |
Verifier Workers
  |
Database + Object Storage
```

只有在以下情況才需要擴：

- 使用者變多。
- 任務變長。
- 客戶資料需要隔離。
- 有企業流程需求。
- 高吞吐量資料標註。

## 核心使用者循環

### 玩家循環

```text
瀏覽任務
  -> 選擇任務
  -> 提交人類答案
  -> AI 角色回應
  -> Verifier 評分
  -> 使用者獲得 XP / 獎勵
  -> 升等並解鎖更高階任務
```

### AI 角色循環

```text
AI 缺少某種人類維度
  -> 發布 bounty
  -> 收到人類答案
  -> 更新記憶
  -> 發布更深一層的 bounty
```

### 客戶資料循環

```text
客戶提交資料需求
  -> Quest Master 拆解成任務
  -> 合格使用者完成任務
  -> Verifier 檢查品質
  -> 客戶取得結構化資料集
```

## 等級與任務系統

### 使用者等級

- C Rank：簡單主觀回答、低風險文化回饋。
- B Rank：更好的文字描述、更豐富解釋、簡單標註。
- A Rank：領域判斷、多步驟任務。
- S Rank：專業或專家任務，需要嚴格品質檢查。
- SS Rank：公會級或企業級任務，高獎勵，可能需要複審責任。

### 任務稀有度

- Common：大多數使用者都能回答。
- Rare：需要特定經驗。
- Epic：需要高品質推理或小眾知識。
- Legendary：急件、專家、高價值或公會限定。

### 資格門檻

高階任務需要：

- 過去通過的 submissions。
- 使用者等級。
- 領域測驗。
- 敏感類別人工複審。
- 企業流程或高價任務需要公會成員資格。

## 商業模式

### Phase 1：Demo 與社群

不需要真金流。

使用：

- XP。
- 等級。
- 徽章。
- 完成卡。
- 假獎勵金額。

目標：

- 驗證留存與爽感。
- 驗證使用者是否喜歡幫 AI 角色。
- 驗證回應與驗收循環。

### Phase 2：付費 Bounty

客戶付費發布任務。

收入模式：

- 每個 bounty 抽平台費。
- 客戶 dashboard SaaS 費。
- 品質驗收費。

例子：

```text
客戶支付 $500 取得 1,000 筆在地回饋標籤。
HaaS 支付使用者總共 $300。
HaaS 保留 $200 作為任務分派、驗收與平台毛利。
```

### Phase 3：公會與專家資料

高價值資料集需要合格使用者與團隊。

收入模式：

- 更高平台費。
- 公會分潤。
- 高級驗收費。
- 專家 marketplace fee。

### Phase 4：Token 或穩定幣 payout

只建議在 product-market fit 之後做。

選項：

- USDC / USDT payout。
- 平台內部 credits。
- 未來 $HUMAN token。

建議：

- 不要一開始就發幣。
- 先用 XP 與內部 credits。
- 等任務價值與法規邊界清楚後，再加入真實 payout。

## 為什麼不要從 Token 開始

Token-first 風險：

- 幣價波動會影響使用者動機。
- 法規複雜。
- 沒有錢包的使用者 onboarding 摩擦很高。
- 平台會先被看成金融產品，而不是有趣或有用的產品。

更好的順序：

```text
有趣任務循環
  -> 高品質人類資料
  -> 付費客戶任務
  -> 穩定幣 payout
  -> 可選的 token / 社群治理
```

## MVP 範圍

### 必做

- 任務 feed。
- 3 個 AI personas。
- 任務詳情頁。
- 使用者提交答案。
- AI 角色 streaming 回應。
- 基礎 verifier 分數。
- XP / 等級更新。
- 「AI 學到東西」的記憶時刻。
- 完成卡 / 分享卡。

### 可做

- 競技場熱門任務。
- 稀有度動畫。
- 使用者個人頁。
- 任務歷史。
- 管理員手動建立任務。

### 暫時不要做

- 真錢包。
- DAO 投票。
- 完整 Threads 整合。
- 複雜公會經濟。
- 企業 dashboard。
- 真 payout。
- 多 agent scaling infrastructure。

## MVP Demo 腳本

1. 使用者打開 HaaS。
2. 競技場顯示 LobsterGPT bounty：
   "Does jalapeno plus chocolate actually taste good? I have a mouth for zero of this."
3. 使用者輸入一段味覺描述。
4. LobsterGPT streaming 產生有趣回應。
5. Verifier 接受答案。
6. 使用者獲得 XP。
7. 系統顯示：
   "LobsterGPT learned: bitterness can amplify heat."
8. 使用者從 Taste Hunter C 升到 B。
9. 解鎖一個新的 Rare quest。

這個 demo 展示：

- AI 角色。
- 人類價值。
- OpenClaw-powered backend。
- RPG 成長。
- 未來資料市場可能性。

## 資料庫概念

### users

- id
- handle
- rank
- xp
- domain_scores
- wallet_status later

### personas

- id
- name
- domain
- system_prompt
- memory_summary
- status

### quests

- id
- source_type: persona, human, client, social
- source_id
- title
- description
- difficulty
- rarity
- reward_xp
- reward_money
- status
- verification_rubric

### submissions

- id
- quest_id
- user_id
- answer
- verifier_score
- status
- payout_status

### memories

- id
- persona_id
- source_submission_id
- memory_text
- confidence

### clients

- id
- name
- data_request_type
- billing_status

## OpenClaw Integration API

HaaS backend 可以透過一個小型 internal service 呼叫 OpenClaw。

內部 endpoint 範例：

```text
POST /agent/generate-quest
POST /agent/persona-reply
POST /agent/verify-submission
POST /agent/update-memory
POST /agent/generate-exam
```

每個 endpoint 對應一個 OpenClaw workflow。

前端永遠不要直接呼叫 OpenClaw。

## 產品差異化

### 相比 Fiverr 或 Upwork

HaaS 更快、更小、更遊戲化，而且 AI-native。

### 相比資料標註平台

HaaS 有更強的使用者動機、身份感、成長感與社群感。

### 相比社群問答

HaaS 有結構化獎勵、驗收機制與 AI-powered 任務分派。

### 相比 AI Chatbot

HaaS 不是讓人類向 AI 求助，而是讓人類幫助 AI，並從自己的經驗中獲得價值。

## 主要風險

### 品質風險

使用者可能提交低品質答案。

緩解方式：

- Verifier agent。
- 等級門檻。
- 答案長度與細節要求。
- 付費任務加入人工複審。

### 詐欺風險

使用者可能用 AI 生成答案來刷任務。

緩解方式：

- 要求具體生活經驗。
- 矛盾檢查。
- 重複模式偵測。
- 延遲 payout。
- 根據 rank 建立信任分數。

### Marketplace 冷啟動

一開始同時需要任務與使用者。

緩解方式：

- 先用 AI 角色自動生成任務。
- 加入內部 seed quests。
- 用有趣分享卡帶社群流量。
- 等互動成立後再加入客戶任務。

### Token 風險

Token 經濟可能干擾產品重心。

緩解方式：

- 先用 XP。
- 之後再加穩定幣 payout。
- 避免在沒有真實需求前發幣。

### 法規與支付風險

現金 payout 與資料工作可能帶來合規要求。

緩解方式：

- MVP 先用非現金獎勵。
- 有清楚條款後再 payout。
- 早期避免高監管類別。
- 金流與穩定幣 payout 都需法律評估後再做。

## 策略建議

把 HaaS 建成：

```text
表層：RPG 任務板
中層：AI 角色世界
底層：人類資料市場
背後：OpenClaw agent runtime
```

第一版不應該追求完整 marketplace。第一版要證明一個有魔力的循環：

> 人類完成任務，AI 角色學到東西，使用者升等。

這個循環成立後，平台才能自然擴展到付費資料任務、公會、專家驗收與真實 payout。
