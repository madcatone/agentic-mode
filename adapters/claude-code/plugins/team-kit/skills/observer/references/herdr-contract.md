# herdr 契約（observer 執行時查）

> 契約事實截至 herdr 0.9.1／2026-10-17 查證（本機 `/opt/homebrew/bin/herdr` 的
> `--help` 與實跑輸出）。控制／查詢類指令回 JSON，統一包 `{id, result}`——資料取
> `.result.*`（例外：`agent read` 回終端原始文本，非 JSON）。版本或輸出不符時，以
> `herdr <cmd> --help` 現場重查為準，不回填本檔以外的記憶。

## 環境閘

- `HERDR_ENV=1` 表示在 herdr 管理環境內。不過 **不得控制任何 pane／agent／workspace**。
- 本檔所有指令都假設閘已過。

## 盤點：`herdr api snapshot`

- 取值路徑：`.result.snapshot`。頂層欄位：`workspaces`／`tabs`／`panes`／`agents`／`layouts`／`focused_pane_id`／`focused_tab_id`／`focused_workspace_id`／`version`／`protocol`。
- `agents[]` 每筆：`agent`（kind，如 claude）、`agent_status`（`idle|working|blocked|done|unknown`）、`cwd`、`pane_id`、`tab_id`、`workspace_id`、`terminal_id`、`terminal_title(_stripped)`、`focused`、`revision`、`state_change_seq`。
- **變化偵測**：`state_change_seq` 與 `revision` 是**每個 agent entry 的欄位**（snapshot 頂層沒有這兩個）——兩輪 snapshot 對同一 agent 比對 seq。
- **`name` 欄位 0.9.1 不出現在 snapshot**（`agent get` 亦無）→ 定位一律 `pane_id`（格式如 `w1:p6`），或先 `agent rename` 賦名後以 name 定位。
- 輪詢即監管：CLI **無 events 子命令**。

## 定位與命名

| 指令 | 語義 |
|---|---|
| `herdr agent rename <target> <name>` | 賦名。規則 `[a-z][a-z0-9_-]{0,31}`；慣例 `<role>` 或 `tk-<role>`。`--clear` 清除 |
| `herdr agent get <target>` | 單筆 agent 資訊（`.result.agent`） |
| `herdr agent list` | 全部 agents（`.result.agents`） |

target 可以是 pane_id 或已賦的 name。**一律顯式傳 target**——省略會落到 UI-focused pane（使用者的終端）。

## 派工

| 指令 | 語義 |
|---|---|
| `herdr agent prompt <target> <text> [--wait] [--until STATUS] [--timeout MS]` | 終端層模擬提交（bracketed-paste＋Enter）。**成功僅代表 bytes 寫入**，不代表理解或接單 |
| `herdr agent send-keys <target> <KEY>...` | 送按鍵（`esc` 是 Escape 正名）。危險——會直接作用在 agent 終端 |
| `herdr pane send-text <pane_id> <text>` | 送純文字（不按 Enter） |
| `herdr pane run <pane_id> <COMMAND>...` | 送文字＋Enter 一次完成 |

`agent prompt` 細節：

- 目標已 blocked → 提交被拒（`agent_blocked`），任何輸入都沒送出。先處理 blocked（回報使用者）再派。
- `--wait`：提交後 5 秒內須觀察到 working 或 blocked，否則回 `agent_prompt_stalled`；之後匹配 `idle|done|blocked`（預設）或 `--until` 指定態（可重複）。**不追蹤 turn**——若提交時 agent 已在 working，該輪完成即可能匹配。
- `--timeout MS`：呼叫端逾時回 `timeout`。
- 長任務：派完即回，交給 /loop 輪詢 snapshot 監管，不做無限 wait。

## 監管

- 每輪 `/loop`：`herdr api snapshot` → 逐 agent 比 `state_change_seq` → 判定（見 SKILL.md §3）。
- 即時等某狀態：`herdr agent wait <target> [--until STATUS] [--timeout MS]`——無 `--until` 匹配 `idle|done|blocked`；**無 `--timeout` 會無限等**，務必帶。approval 警報用 `--until blocked`。
- 讀終端近端輸出（收 status 用）：`herdr agent read <target> [--source visible|recent|recent-unwrapped|detection]`（預設 recent；輸出為**終端原始文本**，非 JSON——解析 status 首行直接 grep 文本）。

## 生命週期

- 開新 agent：`herdr pane split [--current] [--direction right|down] [--cwd <path>] [--no-focus] [--ratio <f>] [--env K=V]` 建 pane → `herdr agent start <name> --kind <kind> --pane <id> [--timeout MS]`。
  - `agent start` 的 pane **必須在 interactive shell prompt**；`--kind` 如 `claude`／`codex` 等；`--timeout` 等互動就緒，預設 30000、上限 300000。成功＝在該終端偵測到預期 agent 且可收輸入。
- **無 `agent stop`**。停一個 agent 只有 `send-keys ctrl+c` 或 `pane close`——都屬危險操作，須使用者明示。
- 收自己的拋棄式 pane：`herdr pane close <pane_id>`（只准關**自己建的**）。

## 危險操作總表

| 操作 | 規矩 |
|---|---|
| 省略 target 的任何 agent／pane 指令 | **禁止**——會打到 UI-focused pane＝使用者的 |
| `herdr server stop` | **禁用** |
| `herdr workspace close`（任何形式；0.9.1 語法 `close <workspace_id>`） | **禁用** |
| 關閉非自建 pane／workspace | **禁止** |
| 對 blocked agent 送任何輸入（含回答 approval） | **禁止**——只回報使用者 |
| `send-keys ctrl+c`／`pane close` 停 agent | 危險操作——須使用者明示 |
| `herdr agent attach`／`focus` | 會搶 UI 焦點——監管不需要，不用 |
