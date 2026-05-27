# HaaS / NemoClaw Handoff

這是 NemoClaw 評審與 demo 操作的主要交接入口。若時間很短，只需要讀這份、`NEMOCLAW_DEMO_RUNBOOK.md`、`SKILL.md`。

## 先開哪個檔案

優先開：

```text
nemoclaw-demo.html
```

這是離線、無 CDN、無 npm、無外部 API 的 demo。它適合 NemoClaw 不能連網或只能讀少量本地檔案的環境。

若要用本機 server：

```bash
python3 -m http.server 8765
```

然後開：

```text
http://127.0.0.1:8765/nemoclaw-demo.html
```

## NemoClaw 要展示什麼

HaaS 的競賽重點不是概念簡報，而是一個可運行的長程代理營運 loop：

```text
scout public signal
  -> policy guardrails
  -> quest draft
  -> approval gate
  -> invite handoff
  -> identity simulation
  -> human submission
  -> verification
  -> reward proposal
  -> audit log
```

## 必讀文件

1. `NEMOCLAW_DEMO_RUNBOOK.md`
2. `SKILL.md`
3. `nemoclaw-system-admin-guide.md`
4. `README.md`

補充文件：

- `haas-web-app-architecture.md`
- `haas-product-business-model.md`
- `openclaw-system-admin-guide.md`
- `README-OPENCLAW-HANDOFF.md`

## 安全邊界

NemoClaw 可以建立草稿、驗收、分類、提出 payout proposal、寫 audit log。

NemoClaw 不能自動：

- 對 Threads 送出 DM、回覆或留言。
- 發布外部社群衍生任務。
- 移動真實資金。
- 暴露個資。
- 處理高風險金融、醫療、法律、安全或失蹤人口案件。
- 封鎖使用者或做懲罰性帳號操作。

## 完整視覺版

`Haas Live Terminal.html` 是較完整的視覺版 demo，但依賴 CDN React/Babel。可連網時可以展示它；受限環境請使用 `nemoclaw-demo.html`。
