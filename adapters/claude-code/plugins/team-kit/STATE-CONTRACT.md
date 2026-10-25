# team-kit 狀態面契約（STATE-CONTRACT）

<!-- last-updated: 2026-10-18 | 事實來源：eng/verify-on-stop.sh、eng/verify.sh、skills/{coder,reviewer,fortify,observer}/SKILL.md；實例抽樣核對 2026-10-18；2026-10-18 收編進 agentic-mode repo（本 plugin 目錄即 kit 根），引用路徑改為 kit 相對 -->

本檔是 team-kit 在 `$AGENT_STATE_HOME`（未設定時 `~/.agent-state`）建立與消費的**全部狀態面
artifact 的單一契約**：每個 artifact 的路徑模式、寫者／讀者、精確行格式、生命週期與併發行為。
所有主張以現行程式碼與 skill 文件為準，逐節附 `檔案:行號` 來源（相對於本 kit 根——即本
plugin 目錄；observer 同收編於 `skills/observer/SKILL.md`）。收編進 repo、plugin 化與跨機
安裝皆以本檔為準；實作與本檔衝突時，以實作為準並修訂本檔。

> **English summary.** This is the single contract for every state artifact team-kit
> keeps under `$AGENT_STATE_HOME` (default `~/.agent-state`): the stop-hook decision
> log, per-agent verify-attempt counters, the most-recent project-root hint,
> per-role machine-readable report files, and the append-only anti-double-post
> ledger for external comments. Each section fixes the path pattern, writer and
> reader, exact line grammar, lifecycle (create / overwrite / delete), and
> concurrency caveats. Every claim is sourced to `file:line` in the current
> scripts and skills and was sampled against live instances on 2026-10-18.

## 1. 總覽

```text
${AGENT_STATE_HOME:-~/.agent-state}/
├── team-kit/                              # kit 執行期狀態（hook 與 worker skills）
│   ├── hook-log.txt                       # stop-hook 每次決定各一行（append-only）
│   ├── root-recent.txt                    # 最近一次開工的專案根（覆寫式，一行一路徑）
│   ├── verify-attempts-<key>.txt          # 被 block 的 stop 計數器（每 agent 一檔，整數）
│   └── reports/                           # 各角色 report（累積，無自動清理）
│       ├── coder/<任務識別碼>-<UTC ts>.md
│       ├── reviewer/<任務識別碼>-<UTC ts>.md
│       └── fortify/<任務識別碼>-<UTC ts>.md
└── reviewer/                              # 對外留言防重貼 ledger
    └── <target>.jsonl                     # append-only，一行一則 JSON
```

注意兩個 `reviewer` 位置不同：`team-kit/reports/reviewer/` 放**審查 report 檔**；
頂層 `reviewer/` 放**對外留言 ledger**。用途與格式互異，勿混。

**AGENT_STATE_HOME 解析**：全部讀寫方統一展開 `${AGENT_STATE_HOME:-$HOME/.agent-state}`
——env 有設用 env 值，未設用 `~/.agent-state`（eng/verify-on-stop.sh:31、
skills/coder/SKILL.md:53-54 與 91、skills/reviewer/SKILL.md:83 與 110、
skills/fortify/SKILL.md:79、skills/observer/SKILL.md:56/120/122）。各元件**各自獨立**展開同一
expression：若某環境地（例：hook 的 shell）與其他環境外設了不同值，狀態會分裂成兩個根，
契約不涵蓋此情境——部署時須全環境一致。預設情境（env 未設）：狀態根＝`~/.agent-state`；
`~/.agent-state/reviewer/` 在首次對外留言前不存在屬正常。

## 2. hook-log.txt — stop-hook 決定 log

- **路徑模式**：`$AGENT_STATE_HOME/team-kit/hook-log.txt`（唯此一檔）。
- **寫者**：`eng/verify-on-stop.sh` 的 `log_line()`（:44-48）——`allow()`／`block()`
  兩個出口都先記一行（:50-51），即 **hook 的每一次決定各一行**；非 coder 家族的
  subagent 停止也會觸發 hook 並記一行 allow（agent_type 判定在 :66-69，此 allow 亦經
  `log_line`）。寫前 `mkdir -p` 狀態目錄（:45）。
- **讀者**：無程式讀者——六個事實來源檔皆無讀取 hook-log 的程序；用途是人類事後稽核。
- **格式**：一行一決定，`<ISO-8601 UTC>|<decision>|<detail>`：
  - 時戳：`date -u +%Y-%m-%dT%H:%M:%SZ`（秒精度、`Z` 結尾，:46）。
  - decision：`allow` 或 `block`（:50-51）。
  - detail：純文字，無轉義。五種 allow 形態——`agent_type=<X|<null>> is not coder`
    （:68）、`last_assistant_message declares status: BLOCKED`（:73）、
    `jq missing—gate inert`（jq 不在 PATH 時的大聲失效：stderr 警告＋此 log 行，
    決定仍為 allow，:61）、
    `verify passed (root=<R>) after <N> prior blocked stop(s); counter cleared`（:135）、
    `max attempts (<M>) reached after <N> blocked stop(s); escalating`（:147）；
    block 形態固定為 `attempt <N>, exit <RC>, key=<K>, root=<R>, summary=<S>`（:159）。
    `root=` 帶解析出的專案根，或字面 `default`（:127）／`stub`（TK_VERIFY_CMD 測試樁，:108）。
  - 欄位分隔：只有前兩個 `|` 是分隔符（printf 三參數，:46）；detail 內可再出現 `|`
    （summary 取自 verify 輸出原文），機器解析時 split 前兩個 `|` 即可。
- **生命週期**：append-only，程式碼無任何 truncate／rotate／刪除——**永久累積**。
  寫入失敗靜默（`2>/dev/null`，:47）、絕不影響 stdout 決定輸出（:16-17）。
- **併發 caveat**：無鎖、無輪替；多 coder 並行停止時各行獨立 append，程式未做進一步保證。
- **來源**：eng/verify-on-stop.sh:16-17, 44-51, 53-62, 66-73, 108, 127, 135, 147, 159。

## 3. verify-attempts-<key>.txt — 被 block 的 stop 計數器

- **路徑模式**：`$AGENT_STATE_HOME/team-kit/verify-attempts-<key>.txt`，`<key>` 見 §3.1。
- **寫者**：僅 `eng/verify-on-stop.sh`。block 決定時以**覆寫**方式寫入遞增後的整數
  （`printf '%s\n' "$new" > "$count_file"`，:152）；首次被擋即建立檔案（值 1）。
- **讀者**：僅 `eng/verify-on-stop.sh` 自己——同一 key 下次 stop 時讀回（:87-90）。
- **格式**：檔案全文＝一個十進位整數＋換行。讀回時空值或非數字一律視為 0（:89）。
- **生命週期**：
  - 刪除時機恰兩條：verify 通過（`rm -f`，allow「counter cleared」，:133-136）；
    達 `TK_MAX_ATTEMPTS` 上限（環境旋鈕，預設 0＝不限制；上限>0 且遞增後超過時
    `rm -f`，allow「escalating」，:144-148）。
  - **不刪除**的路徑：`status: BLOCKED` 逃生口與非 coder agent_type 的 allow 在計數器
    邏輯之前返回（:66-74 先於 :78-83），計數器留存——session 經逃生口結束會留下殘檔。
    程式無自動清掃；殘檔由人類判讀後清理。（實例印證見 §8。）
- **併發 caveat**：不同 agent 不同 key、各自獨立檔案；同 key 併發寫未由程式處理
  （前提是同一 subagent 不會同時觸發兩次 stop）。
- **來源**：eng/verify-on-stop.sh:25-27, 33, 76-90, 132-148, 152。

### 3.1 key 推導規則

hook 對每個 stop 事件推導計數器 key（eng/verify-on-stop.sh:76-82）：

1. `raw` ＝ hook payload 的 `.agent_id`；空則 `.session_id`；再空則字串 `default`（:78-80）。
2. 清洗：`tr -c 'A-Za-z0-9_-' '_'`——不在 `[A-Za-z0-9_-]` 集合的字元逐一代換為 `_`（:81）。
3. 清洗後為空（`raw` 全由外來字元構成時）→ `default`（:82）。

hook 前置判定（與 key 無關但決定計數器是否生效）：`.agent_type` 需匹配
`^coder(-[a-z0-9_-]+)?$`（:66）；`.last_assistant_message` 匹配
`(?im)^\s*status:\s*BLOCKED` 時走逃生口 allow（:72-74）。

## 4. root-recent.txt — 最近專案根 hint

- **路徑模式**：`$AGENT_STATE_HOME/team-kit/root-recent.txt`（唯此一檔）。
- **寫者**：coder skill——**開工第一步**，拿到派工的 `TEAM_KIT_ROOT` 後立刻執行
  `mkdir -p` ＋ `printf '%s\n' "$TEAM_KIT_ROOT" > .../root-recent.txt`
  （skills/coder/SKILL.md:50-55）。
- **讀者**：`eng/verify-on-stop.sh` 的根解析（:111-130），優先序（:8-11, 93-106）：
  1. env `TEAM_KIT_ROOT`（tests／CI 注入）——直接勝出；
  2. hook payload 的 `cwd`——**僅當** `<cwd>/team-kit.json` 存在**且** `jq -e .` 可解析
     （:116-117；巢狀派工的 cwd 是上層 session 的 cwd，通常無 config，不得遮蔽 hint）；
  3. 本 hint 檔——僅當檔案存在且非空（`-s`）時讀**第一行**（`sed -n '1p'`，:119-121）；
  4. fallback：`eng/verify.sh` 自身預設（script 所在 eng/ 的上層＝kit 目錄，verify.sh:16）。
- **格式**：一行＝一個絕對路徑（`%s\n`；覆寫式故恆為單行）。
- **生命週期**：每次 coder 開工**覆寫**；程式無刪除時機。殘值語義＝「最近一次開工的
  專案根」，**不保證**是當前任務的根——上一任務留下的 hint 會被本次解析用到。
- **併發 caveat**：last-writer wins——多 coder 並行於不同根時，後寫者覆蓋先寫者，
  stop 當下可能讀到別的任務的根。個人（單人多案）情境可接受，多工／多機常態化前
  需重盤（eng/verify-on-stop.sh:102-105、skills/coder/SKILL.md:61-62）。
- **來源**：eng/verify-on-stop.sh:8-11, 93-130；eng/verify.sh:16；
  skills/coder/SKILL.md:50-62。

## 5. reports/<role>/ — report 檔契約（machine-readable status 出口）

- **路徑模式**：`$AGENT_STATE_HOME/team-kit/reports/<role>/<任務識別碼>-<UTC ts>.md`；
  `<role>` 目前為 `coder`／`reviewer`／`fortify`（observer 以 `<role>` 泛稱）。
  `<UTC ts>`＝`date -u +%Y%m%dT%H%M%SZ`（秒精度）。目錄由寫者先 `mkdir -p`。
  （skills/coder/SKILL.md:90-94、skills/reviewer/SKILL.md:82-85、
  skills/fortify/SKILL.md:78-80、skills/observer/SKILL.md:56。）
- **任務識別碼**：由 **observer 的素材契約**在派工 prompt 給定——每件派工唯一，
  統一文法 `TK-<issue>`＋後綴（修復輪 `-FIX`、審查軸 `-STD`／`-SPEC`；例
  `TK-29`／`TK-29-FIX`／`TK-29-STD`；observer SKILL.md:51）；兩軸審查由 dispatcher
  給**不同**識別碼（`TK-<issue>-STD`／`TK-<issue>-SPEC`；skills/reviewer/SKILL.md:84-85）。
  coder 的 prompt 未給時自訂 `adhoc-<UTC ts>` 並在回報註明（skills/coder/SKILL.md:95）。
  識別碼同時是聚合時對回各任務的鍵。
- **寫者**（mounting-aware）：
  - coder：收工必做**自寫**（有寫檔能力；skills/coder/SKILL.md:87-97）。
  - reviewer／fortify：**可寫檔的 mounting**（pane／頂層 session）自寫；
    **subagent mounting（唯讀閘門）**寫檔結構性不可行——不繞閘門，以最終訊息交出，
    由 dispatcher（observer）**原文代寫**成 report 檔（不改字、不潤飾、不代填結論），
    並在該回報 Limitations 註明「report 檔未自寫（唯讀閘門 mounting）」
    （skills/reviewer/SKILL.md:86-89、skills/fortify/SKILL.md:81-84、
    skills/observer/SKILL.md:118-121）。
  - 代寫去重：同識別碼已有檔且首行同 status → 不重複寫（skills/observer/SKILL.md:121）。
- **讀者**：observer／herdr 通道——status 的**第一優先**來源（終端視窗內容有限且未必
  逐字）。讀取程序：`ls reports/<role>/` 找該識別碼最新一檔（同名取 ts 最大）→
  `sed -n '1p'` 取首行 status（skills/observer/SKILL.md:122-124）。fallback（report 缺席或
  識別碼對不上）：subagent 通道用最終訊息首行；herdr 通道用 `herdr agent read
  <target>`（視窗有限，讀不到就如實回報，不代填；skills/observer/SKILL.md:125-127）。
- **格式**：檔案內容＝該角色**完整回報＝其最終訊息全文**；**首行必為 status 行**
  （機器解析契約；鍵 `status:` 為英文原字，不得翻譯或改寫）：
  - coder：`status: DONE` 或 `status: BLOCKED`（skills/coder/SKILL.md:72-76）。
  - reviewer（每軸各自一檔）：`status: PASS|FAIL|BLOCKED`，次行起另有
    `reviewer:`／`target:` 等行（skills/reviewer/SKILL.md:58-61）。
  - fortify：`status: PASS`／`FAIL`／`BLOCKED` 擇一（skills/fortify/SKILL.md:57-65）。
  - 聚合時 status 首行**原文引用**、鍵與值不改寫（skills/observer/SKILL.md:135）。
- **生命週期**：累積、無自動清理（各 skill 皆無清理程序）；每次寫入是新檔（新 ts），
  不覆寫既有 report。寫檔（或代寫）失敗**不阻止收工**，但 coder 必須列為風險
  （skills/coder/SKILL.md:93）、reviewer／fortify 必須列入 Limitations
  （skills/reviewer/SKILL.md:90-91、skills/fortify/SKILL.md:85-86）。
- **併發 caveat**：檔名 ts 為秒精度——同識別碼同一秒兩次寫入會撞名覆寫（推論，
  程式與文件均未規範此情境）。
- **來源**：如上各行內標注。

## 6. reviewer/<target>.jsonl — 對外留言 ledger

- **路徑模式**：`$AGENT_STATE_HOME/reviewer/<target>.jsonl`（頂層 `reviewer/`，**不在**
  `team-kit/` 下）；`<target>`＝票號或審查目標識別（skills/reviewer/SKILL.md:110）。
- **寫者**：reviewer 的對外留言流程（§5 人類閘＋ledger）；observer 對外留言沿用
  同一模式與路徑（借契約不重寫；skills/observer/SKILL.md:138-141）。
- **讀者**：貼留言前的同一角色——防重貼查詢（查 target、比 hash）。
- **格式**：JSON Lines，append-only、一行一則、**不改寫既有行**：

  ```json
  {"ts":"<UTC ISO8601>","target":"<票號或審查目標>","hash":"<留言全文 sha256 前 12 碼>","summary":"<≤60 字摘要>"}
  ```

  （skills/reviewer/SKILL.md:112-114）hash 算法：留言全文經
  `printf '%s' "<全文>" | shasum -a 256 | cut -c1-12`——sha256 hex 前 12 碼，
  `printf '%s'` 不帶換行（:116）。
- **生命週期**：僅 append，無自動清理。**三步順序不可換**（:116）：
  (a) 貼前查 ledger 的 target——已記錄即跳過，並在報告寫「已於 `<ts>` 留言過」；
  target 命中但 hash 不同（結論後來改了）→ 停下來問使用者，不自行再貼；
  (b) 人類核准後貼；(c) 貼完立刻 append。
- **併發 caveat**：防重貼是**程序層**保證（三步順序＋貼前查），無鎖——兩個程序並發
  對同一 target 貼留言不受此契約保護。
- **來源**：skills/reviewer/SKILL.md:105-116；skills/observer/SKILL.md:138-141。

## 7. 界外聲明（不屬本契約管轄）

- **專案端暫存**：`eng/verify.sh` 每輪清理 `<TEAM_KIT_ROOT>/<results_dir>`（預設
  `TestResults`，`rm -rf`；verify.sh:35-43）——作用在**專案根**，屬專案端工作目錄，
  不在 `$AGENT_STATE_HOME` 契約內。
- **其他 skill 的 ledger**：`two-axis-review`、`review-response` 等各自 skill 在
  `~/.agent-state/` 下的目錄（本機實存 `two-axis-review/`、`review-response/`），
  屬各 skill 自身的契約，本檔不管轄。
- herdr 的 agent／pane 狀態（snapshot、`state_change_seq` 等）由 herdr 自家管理，亦不在本契約內。

## 8. 實例抽樣核對（2026-10-18，`~/.agent-state/team-kit/`）

- `hook-log.txt`：抽樣 8 行全符合 `<ISO>|<decision>|<detail>`；block 行如
  `2026-10-17T16:19:13Z|block|attempt 1, exit 1, key=adaf5f1241e572511, root=<repo>, summary=verify exited 1 with no diagnostic line`（原實例的 root 已以 `<repo>` 匿名化）
  與 :159 的欄位順序一致；allow 行含 `verify passed (root=...) after 0 prior blocked stop(s); counter cleared`
  與 `last_assistant_message declares status: BLOCKED` 兩型，與 :135／:73 一致。
- `root-recent.txt`：恰一行 `<demo-root>`（單行絕對路徑，覆寫式殘值；原實例的暫存路徑已匿名化）。
- `verify-attempts-*.txt` 三檔：內容各為 `1`／`1`／`4`（單整數）。其中
  `verify-attempts-adaf5f1241e572511.txt`＝4 與 hook-log 同 key 的 4 次 block 後接
  `status: BLOCKED` 逃生口 allow 相符——印證 §3「逃生口不刪計數器」。
- `reports/coder/f4-demo-coder-20261017T174223Z.md`：首行 `status: DONE`；檔名
  ＝`<任務識別碼>-<UTC ts>` 且 ts 符合 `%Y%m%dT%H%M%SZ`。
- `reports/fortify/f4-demo-fortify-20261017T174108Z.md`：首行 `status: FAIL`。
- `~/.agent-state/reviewer/`：不存在（§6 尚無實例；見未確認事項）。

## 9. 未確認事項

1. **ledger 目錄建立方式**：reviewer SKILL.md §5 只給路徑與 append 語義，未明示
   `mkdir -p`；本機亦無 `reviewer/` 實例可對——首次寫入者如何確保目錄存在：未確認。
2. **同識別碼同秒的 report 檔名撞名**：§5 併發 caveat 所述覆寫行為是從 ts 秒精度
   推得的結論，程式與文件均未規範（標記為推論，非實測）。
