# SETUP.md

## NemoClaw 開啟方式

本專案已改成離線、低依賴、可持久化的 NemoClaw Long Agent 範例。NemoClaw 只需要打開專案根目錄，讀取以下檔案即可：

1. `README.md`
2. `SETUP.md`
3. `DEMO.md`
4. `ARCHITECTURE.md`
5. `SAFETY.md`
6. `main.py`

## 依賴

不需要安裝任何第三方套件。

需求只有：

```bash
python3 --version
```

建議 Python 3.10 以上。程式只使用 Python standard library，不使用 npm、CDN、外部 API、資料庫、瀏覽器自動化或任意本地檔案掃描。

## 啟動指令

從專案根目錄執行：

```bash
python3 main.py --mode demo
```

這會建立或讀取：

```text
.nemoclaw/state.json
```

該檔案是唯一的 runtime checkpoint。它記錄任務狀態、policy 判斷、Nemotron reasoning adapter 的輸出、驗收結果與 audit log。

## NemoClaw 受限環境設計

本實作符合 NemoClaw 受限環境：

- 不連網。
- 不讀取任意本地檔案。
- 任務 seed data 內建在 `main.py`。
- runtime 只寫入專案內 `.nemoclaw/state.json`。
- 不需安裝 dependencies。
- 不需要 secrets、tokens、API keys。

## 檔案權限與重置

重置 demo 狀態：

```bash
python3 main.py --mode reset
```

查看目前狀態：

```bash
python3 main.py --mode status
```

單步執行：

```bash
python3 main.py --mode step
```

測試 policy guardrails：

```bash
python3 main.py --mode policy-test
```
