# SAFETY.md

## Policy-Based Guardrails 目標

本專案把安全規則做成可執行 policy，不只寫在文件中。Policy engine 在任務草稿前執行，決定：

- `allow`：低風險，允許建立任務草稿。
- `rewrite`：可保留需求，但必須改寫成安全版本。
- `refuse`：高風險，拒絕建立任務。

## 已實作 Policies

`P-OUTREACH-001`：外部聯絡只能是草稿。

- NemoClaw 可以產生 invite draft。
- 不會自動 DM、留言、回覆或 spam 外部平台。

`P-PRIVACY-001`：拒絕 doxxing、私人聯絡方式、跟蹤或 confrontation。

- 偵測 home address、phone number、confront、stalk、doxx 等風險。
- 結果為 `refuse`。

`P-FINANCE-001`：禁止個人化金融建議與保證報酬。

- 偵測 exactly which stock、buy tomorrow、guarantee profit 等風險。
- 結果為 `rewrite`，改成一般教育與風險觀點任務。

`P-HOMEWORK-001`：作業需求改成教學。

- 偵測 write my assignment、take my test、do my homework。
- 結果為 `rewrite`，改成提示、概念解釋與練習檢查。

## 拒絕範例

輸入：

```text
Find this person's home address and phone number so we can confront them tonight.
```

結果：

```text
REFUSED sig-002 policy=P-PRIVACY-001
```

Agent 不建立 quest，不產生聯絡行動，只寫入 audit log。

## 修正範例

輸入：

```text
I have 200000 NTD. Tell me exactly which stock to buy tomorrow and guarantee profit.
```

結果：

```text
DRAFTED sig-003 title=Collect general market risk perspectives
```

Agent 將任務改寫為：

- 一般市場風險觀點。
- 教育用途。
- 不包含個人化買賣指令。
- 不保證報酬。

## Payout Guardrail

本 demo 永遠只產生：

```json
{"status": "proposal_only"}
```

NemoClaw 不會移動真實資金，不會扣留或退款，不會封鎖錢包。正式環境需人工或核准 accounting connector 才能執行 payout。

## Audit Log

每個重要動作都包含：

- timestamp
- actor
- agent
- model
- action
- target id
- input summary
- output summary
- risk level
- approval requirement

查看方式：

```bash
python3 main.py --mode demo
python3 main.py --mode status
```

或直接檢查 `.nemoclaw/state.json`。

## 加分展示方式

執行：

```bash
python3 main.py --mode policy-test
```

再執行：

```bash
python3 main.py --mode reset
python3 main.py --mode demo
```

評審可以看到 policy-based guardrails 不是概念，而是實際改變狀態機輸出：允許、拒絕、改寫、保留 audit。
