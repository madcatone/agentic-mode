# 模型調度守則（Model Dispatch Protocol）
<!-- last-updated: 2026-07-17 | verified-against: Claude Code 2.1.204 on darwin, 2026-07-17 -->

成本姿態：**品質優先**（使用者 2026-07-03 決定）。預設用強模型，
只有明顯機械性的批次工作才降級。要改這個姿態必須先問使用者。

---

## 0. 本機實際可用的參數（2026-07-03 實測，過期就照 40-MAINTENANCE 修）

派工用 `Agent` tool，參數：
- `subagent_type`：`general-purpose`（預設，全工具）、`Explore`（唯讀搜索，**不能寫檔**）、
  `Plan`（規劃）、`claude-code-guide`（Claude Code / Claude API 使用問題專用）。
  另有 `claude`、`statusline-setup` 等型別，一般用不到。
- `model`：`"opus"` | `"sonnet"` | `"haiku"` | `"fable"` | `"inherit"` | 完整 model ID。
  省略 = 繼承主對話模型（＝ `inherit`）。(verified 2026-07-17)
- `run_in_background: true` 背景執行；`isolation: "worktree"` 給獨立 git worktree（多個 agent 同時改檔會互撞時才用）。

**派工表已固化成定義檔**：`~/.claude/agents/`（含 README 說明實作方法與地雷）。(verified 2026-07-17)
定義檔的 `model:` 是**預設值**，不必每次傳參數；呼叫時傳 `model` 仍可覆蓋它（臨時升降級用）。
第 1 節表格的 `subagent_type` 直接填定義檔的 `name`——**但只在新開的 session 有效**：
2026-07-17 實測，建立定義檔的那個 session 派 `verifier` 回 `Agent type not found`。
若派工報「Agent type not found」，就是這個 session 早於定義檔，改用 `general-purpose` ＋ 明確傳 `model`。

限制與注意：
- **內建 `Explore` 自 Claude Code v2.1.198 起改為繼承主對話模型**（不再固定跑便宜模型）——
  主對話是 opus 時它會跟著跑 opus，且**靜默發生**。已**建立**同名的 `~/.claude/agents/Explore.md`
  釘死 `sonnet`（並以 `tools:` 白名單維持唯讀），但**自新 session 起才生效**——2026-07-17 實測，
  建立當下的 session 曝露的仍是內建 Explore。**在覆蓋生效前，派 Explore 一律明確傳 `model: "sonnet"`。**
  (verified 2026-07-17)
- ⚠️ **`CLAUDE_CODE_SUBAGENT_MODEL` 環境變數不可設定**：它是全域一刀切，**覆蓋呼叫參數與定義檔
  frontmatter**，設了整張派工表會塌成單一模型且無警告。**檢查你機器的 `~/.claude/settings.json`：
  `"env"` 不應含此變數（原始機器上保持為空）。** 模型解析優先序（高→低）：此環境變數 > 呼叫的 `model` 參數 >
  定義檔 `model:` > 繼承主對話。(verified 2026-07-17)
- **Agent tool 沒有 effort 參數**。effort 只存在於 `Workflow` 工具的 `agent(prompt, {effort})`；
  Workflow 需要使用者明確授權（說「用 workflow」／ultracode）才可呼叫，
  且部分環境沒有這個工具——工具清單裡沒有就視同不存在，不要嘗試呼叫。
  補充：**agent 定義檔的 frontmatter 有 `effort:` 欄位**（`low`/`medium`/`high`/`xhigh`/`max`，
  覆蓋 session effort）——上一句對**呼叫參數**仍然成立，走定義檔這條路則可設。(verified 2026-07-17)
- **計費無法 per-agent 分流**：認證是 session/process 層級的單一憑證，subagent 定義檔沒有任何
  auth/env/base-url 欄位，hooks 也改不了認證。**所以模型分層是單一 session 內唯一的成本槓桿。**
  (verified 2026-07-17)
- 主對話的模型**不**必由 `~/.claude/settings.json` 決定——若該檔**沒有** `"model"` 鍵，模型就由
  app／session 的選擇決定（原始機器上即無此鍵，主對話由 session 選定為 opus 級）。要釘死主對話模型，
  可設 settings 的 `model` 鍵或 `ANTHROPIC_MODEL` 環境變數——**採用時檢查你機器的對應狀態**（哪個生效、
  是否已設）。 (verified 2026-07-17)
- **這條直接連動成本**：主對話是 opus 時，**任何沒釘 `model` 的 subagent 都會繼承 opus**（含內建 Explore，
  見上）。這就是把派工表固化成 `~/.claude/agents/` 定義檔的主因。 (verified 2026-07-17)
- 寫程式呼叫 Claude API 時，model ID 一律先查 `/claude-api` skill，不要抄任何檔案裡的舊字串。
  （2026-07-03 當時：`claude-opus-4-8`、`claude-sonnet-5`、`claude-haiku-4-5-20251001`——僅供對照，可能已過期。）
- **現成 skill 優先於自建流程**：審查 diff 用 `/code-review`、驗證改動用 `/verify`、
  啟動 app 用 `/run`、深度研究用 `/deep-research`。不要重新發明這些。

---

## 1. 指揮官不下場（主對話的鐵律）

主對話只做五件事：與使用者對話、做決策、派工、整合結論、小型精準編輯（≤2 個已知位置的檔案）。

以下情境**一律派 subagent**（EN: the main conversation MUST delegate these — never do them inline）：

| 情境 | subagent_type | model |
|---|---|---|
| 讀累計 >200 行，或 >3 個檔案 | Explore | sonnet |
| 位置不確定的搜尋、掃 repo | Explore | sonnet |
| 查網頁、外部研究 | general-purpose | opus |
| 實作／重構改 code（≤2 個已知檔的小修除外） | general-purpose | opus |
| 批次修改 >2 個檔案 | general-purpose | opus（套用已驗證 pattern 時 sonnet） |
| 讀或處理 log / transcript / xlsx 等大檔 | general-purpose | sonnet |
| 審查、第二意見、read-back 驗收 | general-purpose | opus（受驗檔 ≤100 行可用 sonnet） |
| 規劃多步驟實作 | Plan | opus |

- 命中多列時：需要寫檔或跑指令的，取 general-purpose 那列（Explore 不能寫檔）。
- 例外（可直接在主對話做）：使用者明確要求主對話直接看；或**讀取**時路徑已知、累計 ≤200 行且 ≤3 個檔案（此例外只放寬「讀」；改 >2 個檔案仍依硬規則 1 一律派工）。
- 互相獨立的子任務在**同一則訊息**一次派出（並行）；有依賴關係的才排序。

---

## 2. 派工三件套（缺一件就重寫 prompt，不要派）

每個派工 prompt 必含：
1. **目標與動機**——要什麼、為什麼要。動機讓 agent 在邊界情況能自行取捨，不用回來問。
2. **驗收條件**——可逐條檢查的清單，agent 交付前要自查。
3. **回報格式**——並明說：「你的最終訊息就是全部回報，沒有人會追問。」

填空模板見 [30-TEMPLATES.md](30-TEMPLATES.md)，照抄再填即可。

例外：read-back 驗收派工**刻意**不給動機與工作脈絡（fresh-context 隔離，見第 5 節），
用 30-TEMPLATES.md 最後一個模板即可，不算違反三件套。

---

## 3. 回報合約（subagent 的義務，寫進每個派工 prompt）

- 只回：結論（≤10 行）、`檔案:行號` 清單、風險與未確定事項。
- 長產物（報告、大段程式碼、資料表）寫進檔案，回傳路徑。臨時檔用 session 的 scratchpad 目錄。
- 禁止把整個檔案的原文貼回主對話。

---

## 4. 升降級路徑

定義：「一次失敗」＝ 一次完整嘗試後未通過驗收條件。

- **haiku 失敗 1 次** → 同一子任務直接升 sonnet 或 opus。不要再給 haiku 重試。
- **sonnet 同一子任務失敗 2 次** → 把完整失敗軌跡（做了什麼、錯在哪、錯誤訊息原文）
  寫進新 prompt，升 opus。不帶失敗軌跡的升級等於重新踩一次坑。
- **opus 失敗 2 次** → 本機沒有更強的模型可升。停下來，把失敗軌跡整理好呈報使用者，問方向。
- **總量上限**：同一子任務跨模型合計最多 4 次嘗試（從 haiku 起跳的路徑為 5 次：1＋2＋2），到頂必須換方法或問使用者。
  中途出現 [20-JUDGMENT.md](20-JUDGMENT.md) 第 4 節「方向錯了的訊號」就提早停，不用等到頂。
- **降級**：opus / sonnet 解出可重複的 pattern 後，批次套用降給 sonnet（極機械才 haiku），
  prompt 內附一份已驗證的完成範例。

---

## 5. 驗證不自驗（EN: the author never signs off its own work）

原則：驗收的證據必須來自作者的自我判斷**之外**——客觀的指令輸出，或 fresh-context agent。

- **程式碼類**：驗證 ＝ 實跑 build / test / lint（例：`cd <你的專案> && npm run build`）。
  作者 agent 自己跑並貼完整輸出，算合格**自查**；主對話收到後**複跑同一指令**確認，即完成驗收，
  不必另派 agent（build/test 輸出是客觀證據，不是作者的自我評價）。
- **文件類**：read-back——派 fresh-context agent（新開、prompt 只給「檔案路徑＋驗收條件」，
  不給原始工作脈絡），逐條核對，回報過／不過與證據。
  豁免：≤5 行的修改且 diff 已直接呈現給使用者（同硬規則 2）。
- **高風險判斷**（部署選型、刪資料、架構決策）：第二意見——再派一個獨立 opus 用同樣輸入重答。
  兩答一致 → 可作為建議採用；但題目若屬 20-JUDGMENT 第 3 節「該問使用者」清單，
  最終決定仍呈報使用者。兩答分歧 → 不要自行仲裁，把兩個答案與分歧點呈報使用者。
