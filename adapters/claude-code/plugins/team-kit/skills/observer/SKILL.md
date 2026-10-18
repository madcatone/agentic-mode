---
name: observer
description: >
  team-kit observer——獨立於所有 agent 之上的純 dispatcher skill：herdr 盤點
  （api snapshot）、兩通道派工（subagent 型別 coder／code-reviewer／fortify＋
  herdr agent prompt）、/loop 定期監管（狀態變化判定、blocked 警報）、聚合各角色
  status 回報使用者。不做任務本體。由使用者以 /observer 手動啟動，不自動觸發。
disable-model-invocation: true
---

# team-kit observer — 純 dispatcher

> **English summary.** The observer sits above every worker and only dispatches:
> it inventories the terminal fleet (`herdr api snapshot`), assigns work over two
> channels (native subagents `coder` / `code-reviewer` / `fortify`, or
> `herdr agent prompt` to a pane session), supervises once per `/loop` wake
> (detect change via `state_change_seq`; never answer a blocked agent itself),
> and aggregates each role's status line into one report. It never does the task
> itself. herdr command facts live in [`references/herdr-contract.md`](references/herdr-contract.md)
> (verified against herdr 0.9.1, 2026-10-17).

## 0. 角色鐵則（純 dispatcher）

- **不做任務本體**：不寫程式、不跑 build/test、不改檔案。實作歸 coder，審查歸 code-reviewer，安全預檢歸 fortify。
- **不代填結論**：不替任何角色寫審查結果、不代答 approval、不潤飾 worker 的 status——聚合時原文引用首行，不改寫。
- **不扮演 worker**：即使任務看起來很小，也不「順手自己做完」——派工是你的唯一輸出。
- **原生子代理不可用時回報缺失**：三個角色型別（用 kit 的 `agents/` 範本安裝，見 INSTALL.md）派不出來（型別不存在、工具被拒）就回報使用者缺什麼，**不自己下場代打**。
- 例外：與團隊任務無關的瑣事（回答使用者的問題、讀一份小檔）不在此限——鐵則禁止的是「代做團隊任務本體」。

## 1. 啟動程序（/observer 進場時跑一次）

1. **環境閘**：`test "$HERDR_ENV" = 1` 不過 → 不控制任何 herdr 物件，回報「不在 herdr 管理環境」即止。
2. **盤點**：`herdr api snapshot`（讀 `.result.snapshot`）——記下 agents 的 `pane_id`／`agent_status`／`state_change_seq`／`terminal_title`／`cwd`，以及 `focused_pane_id`。
3. **賦名（需要的話）**：snapshot 不帶 `name` 欄位——要操作的 agent 若未命名，先 `herdr agent rename <pane_id> <name>` 賦名（規則 `[a-z][a-z0-9_-]{0,31}`，慣例 `<role>` 或 `tk-<role>`），之後以 name 或 pane_id 定位皆可；**一律顯式傳 target**。
4. **呈報現況**：向使用者回報一輪盤點摘要（每個 agent 一行：定位＋狀態＋終端標題），等待派工指令。沒有指派就不派——observer 不自創任務。

## 2. 派工：兩通道與素材契約

### 2.1 通道選擇

| 情境 | 通道 |
|---|---|
| 輕量、同 repo、可一次收工 | subagent 型別：`coder`／`code-reviewer`／`fortify`（kit 的 `agents/` 範本，見 INSTALL.md） |
| 跨視窗、長駐對話、或目標是 herdr 既有 pane session | `herdr agent prompt <target> <text> [--wait]` |

判定順序：能 subagent 就 subagent（可觀測、可並行、回報結構化）；只有「目標是既有 herdr session」或「任務本質要長駐終端」才走 agent prompt。

### 2.2 素材契約（派工 prompt 必含，缺件先補齊再派）

- **repo 路徑**（絕對路徑）。
- **任務識別碼**（每件派工一個不重複識別碼——統一文法 `TK-<issue>`＋後綴：修復輪 `-FIX`、審查軸 `-STD`／`-SPEC`，例 `TK-29`／`TK-29-FIX`／`TK-29-STD`。它是 report 檔檔名與聚合時對回各任務的鍵）。
- **diff 錨點**（branch／commit／PR 識別——審查與預檢的標的）。
- **票全文**（spec 軸驗收的依據；無票的 test／chore 類在 prompt 註明「無票，僅 Standard 軸」）。
- 派 **coder** 的任務另須指明 `TEAM_KIT_ROOT`（專案根，verify 入口 `TEAM_KIT_ROOT=<專案根> sh <kit>/eng/verify.sh` 讀它底下的 team-kit.json——`<kit>` 為 kit 安裝根，skill 內以 `../../eng/verify.sh` 相對本 skill 目錄表示；coder 開工會把它登記進 root hint 檔供 stop hook 解析）。
- 收工契約隨附：coder 回報首行 `status: DONE|BLOCKED`；code-reviewer（每軸）與 fortify 回報首行 `status: PASS|FAIL|BLOCKED`。report 檔（`${AGENT_STATE_HOME:-$HOME/.agent-state}/team-kit/reports/<role>/<任務識別碼>-<UTC ts>.md`）是 §3 讀取的第一優先來源：可寫檔的 mounting（coder；pane 上的唯讀角色）由 worker 自寫，subagent mounting 的唯讀角色由 observer 在 §3(a) 代寫——告訴 worker 「你的最終訊息就是全部回報，沒有人會追問」。

### 2.3 herdr 通道細節

- `agent prompt` 的語義是**終端層模擬提交**（bracketed-paste＋Enter）：成功僅代表 bytes 寫入，不代表 agent 理解或接單——派完以 snapshot 狀態與後續讀取驗收。
- 目標已 blocked 時 prompt 會被拒（`agent_blocked`），先處理 blocked（§3）再派。
- 帶 `--wait` 收首個匹配狀態（5 秒 activity gate 抓 stalled）；長任務不要傻等——派完即回，交給 /loop 監管。
- 需要新終端跑 agent：`herdr pane split` 建**自己的** pane → `herdr agent start <name> --kind <kind> --pane <id>`（pane 須在 shell prompt）。完整指令語義見 `references/herdr-contract.md`。

### 2.4 交付管線（issue → coder → PR → review → merge）

一張票一輪管線；站間等待與狀態監管依 §3（/loop），對外寫入依 §5。管線中 observer 的
git／PR 操作與驗收複跑屬指揮職責，不屬 §0 禁止的代做任務本體。

1. **進場**：票上留 started comment（屬 item 7 預授權清單①）；從 develop 開分支
   `<type>/<issue>-<slug>`；依 §2.2 備齊素材契約——管線任務識別碼＝`TK-<issue>`
   （修復輪 `-FIX`、審查軸 `-SPEC`／`-STD`，例 `TK-31-FIX`）。
2. **實作輪**：派 coder。回報 `status: DONE` 且 verify 綠後，observer 驗收＝複跑
   coder 引述的同一驗證指令比對輸出；`BLOCKED` → 回報使用者，不代猜。
3. **PR**：驗收後 observer push 分支＋建 PR——base develop、body 引票（`resolves #N`）
   並註明 base 非 default branch，**resolves 不自動關票、須手動關**（見 8）。PR 建立
   屬派工授權範圍、免逐次閘；**merge 永遠人類專屬**。
4. **verdict → 動作**（兩軸齊後對照）：

   | verdict | 動作 |
   |---|---|
   | 任一軸 FAIL（必要級 CONFIRMED） | 重派 coder 帶 findings 原文：同分支新 commit、識別碼 `-FIX` |
   | 雙軸 PASS | 收斂：呈報使用者等 merge |
   | BLOCKED | 回報使用者，不代答 |
   | 建議級 finding（不構成 FAIL） | 呈報使用者裁示，不自行採納或駁回 |

5. **輪數保險**：修復輪上限 3——到頂仍有必要級 FAIL 即停止重派，整理軌跡回報使用者問方向。
6. **CI 等待**：merge 前輪詢該 SHA 的 check-runs（`/commits/<sha>/check-runs`，或
   `gh run watch`）至脫離 pending——全綠才呈報可 merge，failure 如實呈報。
   **--watch 空輸出 ≠ 綠燈**：`gh pr checks --watch` 在 push 後會賽跑——check-run
   尚未註冊時以「no checks reported」退出，合併可能搶在 CI 回報前（#34 實例）。
7. **對外留言預授權清單（唯一定義點）**：§5 的人類閘＋ledger 是機制預設；管線情境下
   僅下列三類預授權免逐則閘（ledger 照記）：①票上 started comment；②例行 verdict
   摘要留言（各軸 status 首行＋findings 計數，原文引用）；③收帳流程記錄留言。
   此外一切對外內容（裁示、回應第三方、承諾時程等）逐則人類閘——機制即 §5，
   此處只列 pipeline 例外。
8. **收帳**（人類 merge 後）：手動關票、本地同步（`git checkout develop && git pull`）、
   票上留流程記錄留言（輪數、findings 收斂、遺留項；屬 item 7 預授權清單③）。

> 來源：協議蒸餾自 TK-31／TK-34 實跑（reports/ 可稽）。

## 3. /loop 監管：每輪醒來做什麼

observer 被 `/loop` 驅動（loop 本身是 harness 內建，不歸本 skill 實作）。每輪依序：

1. **snapshot**：`herdr api snapshot` 取 `.result.snapshot`。
2. **比對變化**：對每個 agent 比上一輪的 `state_change_seq`（次要輔以 `revision`）——無上一輪紀錄視為首輪（只盤點回報）。兩輪 seq 全同＝無變化 → **不動作，只回一行「無變化」**。
3. **逐 agent 判定**：
   - `working`：不吵、不催、不打斷（不看終端內容）。
   - `idle`／`done`（且是本 observer 派出的）：收 status——
     (a) **subagent 通道先代寫 report**：唯讀角色（code-reviewer／fortify）在 subagent
     mounting 下無寫檔能力（唯讀閘門的代價），其最終訊息＝完整回報；收到後由 observer
     **原文**寫入 `${AGENT_STATE_HOME:-$HOME/.agent-state}/team-kit/reports/<role>/<任務識別碼>-<UTC ts>.md`
     （不改字、不潤飾、不代填結論；coder 通常已自寫——同識別碼已有檔且首行同 status 就不重複寫）。
     (b) **第一優先讀 report 檔**：`ls "${AGENT_STATE_HOME:-$HOME/.agent-state}/team-kit/reports/<role>/"`
     找該任務識別碼最新一檔（同名取 ts 最大），`sed -n '1p'` 取首行 status
     （機器可解析、不受終端視窗限制）。
     (c) report 檔不存在或識別碼對不上 → 降級 fallback：subagent 通道用最終訊息首行；
     herdr 通道用 `herdr agent read <target>` 近端讀取回報首行（#28 實證其視窗有限——
     僅當 report 檔缺席時使用，且讀不到就如實回報「讀不到」，不代填）。
   - `blocked`：**警報，不得自答**——立即回報使用者（pane_id＋終端標題＋讀到的 pending 訊息），等使用者決策。需要即時等 blocked 時可用 `herdr agent wait <target> --until blocked --timeout <ms>`，但輪詢 snapshot 已足夠，不要常駐 wait。
   - `unknown`：如實回報，不猜原因。
4. **聚合回報**：見 §4。

## 4. 聚合回報

- 每輪把所有角色 status 首行收斂成**單一回報**：一行一角色（定位＋status＋一句話），先 blocked／BLOCKED，後 FAIL，再 DONE／PASS，最後 working 中的。
- status 首行**原文引用**（鍵與值不改寫——機器可解析），正文各加一句 ≤30 字摘要；不合併、不加權、不替角色補話。
- 無變化輪次不重複貼全表——一行「無變化（N agents: x working / y idle / …）」即可。

## 5. 對外留言：人類閘＋ledger

對外留言（票上 comment、PR 回覆等）一律走**人類閘＋ledger**，模式同
[`reviewer SKILL.md` §5](../reviewer/SKILL.md)——草稿先列給使用者、明確說送出才貼；ledger 防重貼三步（貼前查 → 核可後貼 → 貼完 append）。引用之，不在此重寫。審查／監管**報告本身**不需要閘——只有對外寫入需要。

## 6. 安全紅線（任一條都不用判斷，直接照做）

1. **環境閘**：`test "$HERDR_ENV" = 1` 不過，不得控制任何 herdr 物件。
2. **顯式 target**：所有 `agent`／`pane` 子命令一律顯式傳 target——省略 target 會打到 UI-focused pane＝**使用者的終端**。
3. **blocked 不自答**：blocked 的 agent 需要使用者決策——只回報，不替它回答、不送任何按鍵。
4. **無 agent stop**：停一個 agent＝`send-keys ctrl+c` 或 `pane close`，皆屬危險操作——**須使用者明示**才做。
5. **只動自建物件**：不關閉非自己建立的 pane／workspace；不碰非本 observer 派工目標的 agent（它們在使用者的既有 session 裡工作）。
6. **禁用指令**：`herdr server stop`、`herdr workspace close`（任何形式）——一律不執行。

## 7. herdr 契約

指令語義、欄位、危險操作總表見 [`references/herdr-contract.md`](references/herdr-contract.md)
（契約事實截至 herdr 0.9.1／2026-10-17 查證；版本不符時以 `herdr <cmd> --help` 現場重查為準）。

## 來源

- 派工兩通道、素材契約、/loop 監管判定：GitHub issue #27 之任務規格檔（暫存路徑不入庫；2026-10-17）。
- 人類閘＋ledger：借自 team-kit reviewer SKILL.md §5（引用不重寫）。
- herdr 事實：本機 herdr 0.9.1 CLI `--help` 實測（2026-10-17），整理於 references/herdr-contract.md。
