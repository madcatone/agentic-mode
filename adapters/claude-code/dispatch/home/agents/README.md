# `~/.claude/agents/` — 派工制度的定義檔
<!-- last-updated: 2026-07-17 | verified-against: Claude Code 2.1.204 on darwin -->

## 這個目錄是什麼、為何存在

把 [`../rules/10-DISPATCH.md`](../rules/10-DISPATCH.md) 第 1 節的派工表**固化成檔案**。

在此之前，制度完全靠每次呼叫 `Agent` tool 時記得傳對 `model` 參數——會漏。
更關鍵的是 **Claude Code v2.1.198 起，內建 `Explore` 改為繼承主對話模型**（不再固定跑便宜模型）：
主對話是 Opus 時，每次 Explore 搜尋都會跟著跑 Opus，比制度預期貴得多，而且**靜默發生**——
沒有任何錯誤訊息會告訴你成本跑掉了。

本目錄同時解決這兩件事：定義檔的 `model:` 是**預設值**，不必每次傳參數也不會漏；
同名的 `Explore.md` 覆蓋內建定義，把它釘回 sonnet。

`~/.claude/agents/` = 全域可用（所有專案）。`<repo>/.claude/agents/` = 該 repo 專用，可覆寫全域同名定義。

---

## 定義檔 ↔ 10-DISPATCH 第 1 節派工表 對照

| 10-DISPATCH 表的列 | 定義檔 | model | 備註 |
|---|---|---|---|
| 讀累計 >200 行，或 >3 個檔案 | `Explore.md` | sonnet | 覆蓋內建，唯讀 |
| 位置不確定的搜尋、掃 repo | `Explore.md` | sonnet | 同上 |
| 查網頁、外部研究 | `researcher.md` | opus | |
| 實作／重構改 code | `implementer.md` | opus | `effort: high` |
| 批次修改 >2 個檔案（套用**已驗證** pattern 時） | `bulk-editor.md` | sonnet | 無已驗證範例時該退回 `implementer` |
| 批次修改 >2 個檔案（一般情況） | `implementer.md` | opus | |
| 讀或處理 log / transcript / xlsx 等大檔 | `log-digger.md` | sonnet | |
| 審查、第二意見 | `reviewer.md` | opus | |
| read-back 驗收 | `verifier.md` | opus | 唯讀，fresh-context |
| 規劃多步驟實作 | 內建 `Plan` | — | **無定義檔，見下方「已知缺口」** |

`subagent_type` 填定義檔的 `name`（＝檔名去掉 `.md`）。

### 兩個刻意的設計決定（推論，非官方規定）

1. **`Explore` 與 `verifier` 用 `tools:` 白名單鎖成唯讀**。Explore 是因為 10-DISPATCH 明文
   「Explore 不能寫檔」；verifier 是因為驗收者一旦動手修，就變成作者，硬規則 3
   （作者不簽收自己的產出）當場失效。白名單留了 `Bash`（唯讀查詢用：`grep`、`git show`、`ls`）。
2. **定義檔保持「薄」**——只放角色紀律與**指向** `30-TEMPLATES.md` 的引用，
   **不複製模板內容**。依據 LESSONS 2026-07-11：分發鏈雙副本會各對一半，
   維持單一事實源比就近方便重要。派工時仍由呼叫端填模板。

---

## 模型解析優先序（事實，見文末來源）

高 → 低，先命中者勝：

1. `CLAUDE_CODE_SUBAGENT_MODEL` 環境變數 ⚠️（見下方警告）
2. 呼叫 `Agent` tool 時傳的 `model` 參數
3. 定義檔 frontmatter 的 `model:`
4. 繼承主對話模型（`model:` 省略或寫 `inherit` 時）

**第 2 項高於第 3 項是刻意保留的**：定義檔給的是預設值，不是牢籠。
臨時要升降級（例：這次的 Explore 任務特別難，想用 opus）就在呼叫時傳 `model: "opus"` 覆蓋，
不必改檔。升降級的判準見 10-DISPATCH 第 4 節。

### ⚠️ `CLAUDE_CODE_SUBAGENT_MODEL` 是地雷，不可設定

它是**全域一刀切**：覆蓋 per-invocation 參數**與**定義檔 frontmatter。
一旦設了，整張派工表會塌成單一模型——Explore、implementer、reviewer 全部跑同一個 model，
而且**不會有任何警告**，你只會在帳單或品質下滑時才發現。

目前 `~/.claude/settings.json` 的 `"env": {}` 為空，**保持這樣**。
唯一合理的使用情境是「臨時要全面降級跑一批機械工作」，用完**立刻設回 `inherit` 或移除**。

---

## 計費限制：模型分層是目前唯一的成本槓桿（事實）

**無法讓不同 subagent 走不同的 API 帳號／金鑰。** 認證是 **session/process 層級的單一憑證**：
subagent frontmatter 沒有任何 auth / env / base-url 欄位，hooks 也改不了認證。
所有 subagent 一律沿用啟動該 session 的憑證。

推論（非官方）：真的要讓不同工作走不同 API 帳號，只能**開兩個獨立的 session**，
各自 `export` 不同的環境變數後啟動——不存在 session 內分流的做法。

因此在單一 session 內，**選對 model 是唯一能拉的成本槓桿**，這正是本目錄存在的意義。

---

## 維護方式

- **新增／改名 agent：要新開 session 才認得。** 官方文件說會自動偵測檔案變更、數秒生效，
  但 **2026-07-17 本機實測：執行中的 session 認不到新定義檔**——在建立本目錄的那個 session 裡派
  `subagent_type: verifier`，回 `Agent type 'verifier' not found`，且該 session 曝露的 `Explore`
  仍是**內建版**（description 與 tools 都與本目錄的 `Explore.md` 不符），證明覆蓋未生效。
  **未確認**：修改**既有**定義檔的內容（非新增）是否會熱載入。保險做法：改完就重開 session。
- 目錄**遞迴掃描**——可以用子目錄分類，不影響識別。
- **`name` 必須全樹唯一**（跨 `~/.claude/agents/` 與 `<repo>/.claude/agents/`）。
  新增定義檔前先確認名稱沒撞。
- 要**覆蓋內建 agent**（如 `Explore`），定義檔的 `name` 必須與內建**完全同名**。
- 改動本目錄的定義檔＝改動派工制度的一部分。**改 model 分層、加減 agent 前，
  照 [`../rules/40-MAINTENANCE.md`](../rules/40-MAINTENANCE.md) 第 1 節判斷是否需要先問使用者**
  （成本姿態與升降級門檻屬「必須先問」類）。

### frontmatter 完整欄位（事實）

`name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`,
`skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`

- `model:` 接受別名 `sonnet` / `opus` / `haiku` / `fable`、完整 model ID、或 `inherit`；省略 ＝ `inherit`。
- `effort:` 接受 `low` / `medium` / `high` / `xhigh` / `max`（覆蓋 session effort）。
  注意這是**定義檔**的欄位；`Agent` tool 的**呼叫參數**仍然沒有 effort（10-DISPATCH 第 0 節那句仍正確）。
- `description` 會被 Claude Code 用來自動選 agent，所以寫準確；
  但本制度的預設用法是**明確指定 `subagent_type`**，不依賴自動選擇。

---

## 已知缺口（待使用者裁決）

- **`Plan`（opus）沒有定義檔**。10-DISPATCH 表列了「規劃多步驟實作 → Plan / opus」，
  但本次只建立了 7 個定義檔。內建 `Plan` 是否也如 `Explore` 一樣改為繼承主對話模型，**未確認**。
  若要釘死成 opus，需要建 `Plan.md` 同名覆蓋——但覆蓋內建會**取代**它原有的系統提示
  （內建的規劃提示詞不公開），可能失去內建行為。**這個取捨未經使用者決定，故未做。**
  現況：呼叫 `Plan` 時請照 10-DISPATCH 明確傳 `model: "opus"`。

---

## 來源與查證日期

- 事實部分（frontmatter 欄位、model/effort 可填值、模型解析優先序、`CLAUDE_CODE_SUBAGENT_MODEL`
  的全域覆蓋行為、目錄位置與遞迴掃描、自動偵測變更、`name` 唯一性、v2.1.198 的 Explore 變更、
  認證為 session 層級單一憑證）：**Claude Code 官方文件**
  <https://docs.claude.com/en/docs/claude-code/sub-agents> 及設定文件
  <https://docs.claude.com/en/docs/claude-code/settings> **(verified 2026-07-17)**。
- 本機 Claude Code 版本：**2.1.204**（`claude --version`, 2026-07-17）。
- **推論**（無官方來源，我的判斷）：唯讀白名單的設計理由、「開兩個 session 分流 API」的做法、
  定義檔保持薄的理由、`Plan` 覆蓋的取捨分析。以上均在文中標為推論。
- **未確認**：內建 `Plan` 是否也繼承主對話模型（見「已知缺口」）。
