# 跨 harness mounting 註記（唯讀保證）

本 skill（SKILL.md＋references/）以**能力描述**表達一切工具需求：**唯讀 shell、檔案讀取、搜尋、委派子代理**。全文不寫死任何 harness 專屬工具名——任何 harness 可把本目錄直接當規則檔載入。

攜帶方式：**整個 team-kit 目錄一起帶**。skill 以 kit 相對路徑引用內部檔案（`../../rules/team-rules.md`、`../../eng/reviewer-git-only.sh`），目錄結構完整即處處可解析。

## 唯讀保證的分層（至少一層成立，建議兩層）

1. **工具白名單層**：harness 層只授予唯讀能力——檔案讀取、搜尋、glob、受限的指令殼。
2. **閘門／沙箱層**（二擇一）：
   - **hook 閘門**：kit 隨附 `eng/reviewer-git-only.sh`——對指令類呼叫把關：唯讀 git 七白名單（status／diff／log／show／ls-files／blame／rev-parse）放行，可帶 `git -C <dir>`（值限安全路徑字元集）與 `--no-pager` 前綴（repo≠cwd 掛載用）；shell 複合語法（管道、重導、替換等）與可寫檔／可執行輔助器的旗標 deny；hook 輸入解析失敗 deny；**非指令的讀取類呼叫靜默放行**。
   - **read-only 沙箱**：harness 原生沙箱在更高層限制寫入與執行。

## 各 harness mounting

| harness | 掛法 | 備註 |
|---|---|---|
| Claude Code | agent 定義檔（kit 隨附 `code-reviewer`，放該 harness 的 agents 目錄）：工具白名單＋PreToolUse hook（matcher 指向**指令殼類工具事件**）掛 reviewer-git-only.sh | matcher 字串與 hook 設定由 agent 定義檔攜帶——harness 專屬設定不進本 skill（中立性） |
| VS Code Local | 同樣掛 hook，但此 mounting **忽略 hook matcher**——每個工具呼叫都會進 hook | 靠腳本自身分支把關：讀取類靜默放行、寫入／執行類 deny；不能依賴 matcher 過濾，正因如此腳本才自帶分支 |
| Codex | 以原生 read-only 沙箱執行 reviewer，可**不掛 hook** | 沙箱已在更高層保證唯讀；skill 內容直接載入即可 |

共同底線：無論哪種 mounting，reviewer 不得取得寫檔或執行任意指令的能力。mounting 只決定「唯讀由哪一層保證」，**不影響審查程序本身**——程序一律照 SKILL.md 走。

被閘門擋下指令時的行為：不繞道、不換寫法重試、不要求放行——照 SKILL.md §3 回 `status: BLOCKED`，Limitations 記被擋的指令與缺的證據。
