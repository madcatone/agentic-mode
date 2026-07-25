# Claude 派工套件（dispatch kit）

某台機器 commander-mode 派工系統的**定時釋出快照**——包含機器級操作規則
（`CLAUDE.md` + `rules/`）與 `~/.claude/` 下的 subagent 派工定義檔（`agents/`）。
裝上去之後，同事的 Claude Code session 就會繼承同一套「重派工」操作模型：主模型
負責對話、決策、派工、整合結論；大量讀檔、repo 掃描、批次修改則交給分層 subagent，
而它們只回結論。

> 繁體中文版。English: [README.md](README.md) — informationally equivalent.

## 與 `fable5` 的關係

[`fable5`](../plugins/fable5) plugin 與這個套件是**通往同一套操作模型的兩條路**，兩者
互補：

- **`fable5` 出的是 *founding prompt*** ——你花一個強模型 session，從你自己機器的實況
  （settings、repos、工具）出發，從零長出整套規則檔。
- **dispatch kit 出的是 *演化完成的成品*** ——這台原始機器已經花了很多 session 養出來
  並打磨過的規則檔（它們會持續透過自己的 `LESSONS.md` 演化）。把它們丟進 `~/.claude/`
  就可以直接採用結果，不需要 founding session。

想自己養一套，用 `fable5`；想直接採用一份實戰過的版本、然後再讓它繼續透過*你的*
`LESSONS.md` 演化，用 dispatch kit。

## 快照定位與同步紀律

- **本套件是 `2026-07-25` 的快照。** 這是一個時間點的拷貝，不是 live feed。本次刷新
  在 `CLAUDE.md` 補上 **標準行為** 節（gcm commit／PR 慣例，用來壓掉 harness 內建的
  `Co-Authored-By` 預設），並鏡射原始機器的懶載入拆分，把 `00-DIAGNOSIS.md` 與
  `LESSONS.md` 從常駐的 `rules/` 移到按需讀取的 `rules-ref/`。
- **正典位於原始機器的 `~/.claude/`。** 那一份會持續演化（往 `LESSONS.md` 追加、隨
  harness 改動而修訂 `rules/`）。本套件不會。
- **要更新本套件：** 從原始機器的 `~/.claude/` 重新打包（重跑一次去個資 pass），把快照
  日期 bump。本 repo **沒有** upstream sync——這個套件**不**屬於
  `scripts/sync_plugins.py`，因為它的正典位於原始機器，不在本 repo。
- **你的在地演化留在在地。** 安裝之後，那個 `~/.claude/` 就是*你的*：把你自己學到的
  lesson 追加到你自己的 `LESSONS.md`，為你自己的環境調整規則。**不要**嘗試把你的修改
  回流到本套件或原始機器。

## 安裝

套件的 [`home/`](home) 目錄鏡射了 `~/.claude/` 底下應該存在的內容。安裝 = 先備份你
現有的東西，再把 `home/` 的內容拷貝進去。它只會寫入 `CLAUDE.md`、`rules/*.md` 與
`agents/*.md`；絕不碰你的 `settings.json`、`projects/` 或 `~/.claude/` 的其他任何東西。

從**這個目錄**（`adapters/claude-code/dispatch/`）執行。

### bash / zsh（macOS、Linux）

```bash
# 1) 備份既有的東西（不存在則略過）
ts=$(date +%Y%m%d-%H%M%S)
for p in ~/.claude/CLAUDE.md ~/.claude/rules ~/.claude/rules-ref ~/.claude/agents; do
  [ -e "$p" ] && cp -R "$p" "$p.bak-$ts"
done

# 2) 把套件合進 ~/.claude（只新增/覆寫套件提供的檔案）
mkdir -p ~/.claude
cp -R home/. ~/.claude/
```

### PowerShell（Windows）

```powershell
# 1) 備份既有的東西（不存在則略過）
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($p in @("$HOME\.claude\CLAUDE.md","$HOME\.claude\rules","$HOME\.claude\rules-ref","$HOME\.claude\agents")) {
  if (Test-Path $p) { Copy-Item $p "$p.bak-$ts" -Recurse -Force }
}

# 2) 把套件合進 ~\.claude（merge-safe：先建目錄，再遞迴拷貝）
New-Item -ItemType Directory -Force -Path "$HOME\.claude" | Out-Null
Copy-Item -Path "home\*" -Destination "$HOME\.claude" -Recurse -Force
```

新增或改名的 `agents/` 定義檔**只在重新開啟的 session 中生效**——安裝後請重啟 Claude
Code（詳見 `home/agents/README.md` 的備註）。

## `settings.json` 指引（自己設；套件不會幫你改）

本套件刻意不附 `settings.json`。請手動設定下列幾項：

- **保持 `"env"` 裡沒有 `CLAUDE_CODE_SUBAGENT_MODEL`。** 這個變數是全域 override——它會
  同時蓋過呼叫端的 `model` 參數**和** agent 定義檔 frontmatter，設下去等於把整張派工
  表塌成單一 model，而且毫無警示。請保持未設定。
- **品質優先的成本姿態。** 規則預設使用強模型，只有面對明顯機械性的批次工作才降級。
  若你想要更便宜的預設值，那是一個刻意的姿態調整——見 `rules/10-DISPATCH.md`。
- **建議設 `permissions.defaultMode: "auto"`。** 它讓分類器代替逐次彈窗來核可例行動作；
  分類器不可用時，CLI 會自動退回一般的 `default` 逐次詢問，不會降低你的最後防線。這契合
  重派工的操作模型——派工迴圈上少被打斷。
- 規則已在 Claude Code `2.1.204`、darwin 上驗證（2026-07-17）。在更新的 build 上，
  請重新驗證 `rules/10-DISPATCH.md` §0 裡的 harness 事實。

## 安裝後的機器調適清單

原始機器的私人交接信被刻意**排除**於本套件之外。它的工作——告訴你哪些地方要適應
*你的*環境——改由這份清單承擔。安裝後請完整走一次：

1. **換掉 build/test 指令。** 規則用 `cd <你的專案> && npm run build` 當 placeholder。
   把它（在你的習慣裡，以及寫派工 prompt 時）換成你專案實際的 gate 指令。
2. **依賴 `agents/` 前先重啟。** 定義檔只有在它們安裝*之後*啟動的 session 才會被讀到。
3. **稽核你自己的權限 allowlist。** 原始機器的一個 lesson：它的 `settings.local.json`
   allowlist 比理想寬（例如無限制的 `ssh`），而 harness *不會*替你把關高風險動作。
   讀一遍你自己的 `~/.claude/settings*.json`，確認那些自動核可的項目你都能接受——
   規則假設*你*是最後一道防線。
4. **你的 `memory/` 從空白開始。** 規則引用了一個 per-project memory 機制（專案事實 +
   `MEMORY.md` 索引）。套件不附內容——那是你在每個 repo 工作時自己累積的。
5. **重新查證 harness 事實。** `rules/10-DISPATCH.md` §0 記錄了 subagent 參數、model
   解析順序、Explore 的繼承行為，這些都是在某個特定 Claude Code build 上觀察到的。若
   你的情況不同，依 `rules/40-MAINTENANCE.md` §5 修正該檔，並標記 `(verified <date>)`。
6. **個人 `~/.claude/skills/` 別跟 team plugin skill 重複。** 若某個 skill 已經以 team
   plugin 形式發佈，就讓它留在那裡當單一事實源；在 `~/.claude/skills/` 底下再放一份個人
   拷貝，只要任一邊改動就會開始漂移。

## 從原始機器改編了什麼

為了讓快照可攜，去個資 pass 做了下列處理：

- **移除**所有絕對 home 路徑、IP literal、內部主機名稱與憑證（這些檔案裡本來就沒有
  後者）。
- **一般化** `rules/` 裡的專案特定範例（特定的 feature ID、部署廠商、某個特定的
  spec-browser 專案、`poc/` 的 build 指令），改成保留教學價值的通用描述。
- **重新標記** `00-DIAGNOSIS.md` 的「本機證據」區塊為「原始機器上的實例（採用時對照
  你自己的環境）」。
- **整理 `LESSONS.md`**：只保留在別的 repo 仍然成立的 lesson（內部 repo 名稱、ticket
  /MR 號、內部工具名稱都已一般化）；剔除只屬於原始機器自己 pipeline 的條目。Append-only
  的格式與日期都保留。
- **完整排除 `50-LETTER.md`**（原始機器的私人交接信），並從 `CLAUDE.md` 移除它的
  routing-table 那一列。

`~/.claude/…` 相對路徑則原樣保留——它們在每位同事的機器上都以同樣方式解析。

## 內容

```
dispatch/
  README.md            # 本檔（英文）
  README-ZH.md         # 繁體中文（等價）
  home/                # 鏡射 ~/.claude/ —— 安裝 payload
    CLAUDE.md          # 機器級路由器 + 6 條硬規則 + 標準行為
    rules/             # 每個 session 常駐載入
      10-DISPATCH.md   # model 派工協議、subagent 參數、成本控制桿
      20-JUDGMENT.md   # 判斷準則（done-ness、何時該問、品質底線）
      30-TEMPLATES.md  # 填空式派工 prompt 模板
      40-MAINTENANCE.md# 如何在不讓規則腐爛的前提下演化它們
    rules-ref/         # 按需讀取（不進常駐 context）
      00-DIAGNOSIS.md  # 每個規則檔所要修復的三種失敗模式
      LESSONS.md       # 經過整理、append-only 的田野 lesson
    agents/            # subagent 定義檔（以檔案形式呈現的派工表）
      README.md        # 定義檔如何運作 + 已知缺口
      Explore.md implementer.md reviewer.md verifier.md
      researcher.md bulk-editor.md log-digger.md
```
