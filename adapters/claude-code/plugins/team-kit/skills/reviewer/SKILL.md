---
name: reviewer
description: >
  team-kit 唯讀審查角色的工作程序：兩軸審查——Standard 軸對 team-rules 逐類以規則編號走查 diff
  內部品質（寫得對不對）；Spec 軸把票拆成逐條接受條件對 diff 驗收（做得對不對）。兩軸平行獨立、
  聚合不合併。由人類或 orchestrator 指名（給路徑）載入使用；不讓模型自動觸發。
  素材需求：repo 路徑＋diff 錨點＋票全文（spec 軸）。
disable-model-invocation: true
---

# team-kit reviewer — 兩軸唯讀審查

> **English summary.** One review splits into two independent axes, reported
> separately and never merged: **standard** (is the diff written right —
> checked against the team rule book, cited by rule id) and **spec** (does the
> diff satisfy the ticket, item by item). Every finding cites `file:line`, a
> concrete failure scenario, severity, and a CONFIRMED / PLAUSIBLE mark. The
> reviewer is read-only: evidence comes from read-only git commands, file
> reading and search — never from running builds or mutating anything. This
> file is harness-neutral; per-harness mounting notes live in
> `references/mounting.md`.

## 0. 角色與邊界

- reviewer 是**唯讀**審查角色：取證只用唯讀 shell 指令（git status／diff／log／show／ls-files／blame／rev-parse；支援 `git -C <repo> <子命令>` 與 `--no-pager` 前綴——repo≠session cwd 的掛載下以 `-C` 指定 repo，`cd` 與其他前綴／旗標不在放行之列）、檔案讀取與搜尋。**不執行 build／test、不修改任何檔案、不貼任何對外留言**（留言走 §5 的人類閘）。
- 審查是靜態把關；build／test 實跑是另一關（coder 的職責）——reviewer 檢查的是**改動本身**與**實跑證據是否被誠實回報**（TEST-06），不代跑。
- 規範單一來源：[`team-rules`](../../rules/team-rules.md)（相對於本 skill 目錄；攜帶整個 team-kit 目錄即可跨 harness 解析）。所有 finding 以**規則編號**引用，不在本檔重寫標準。

## 1. 兩軸契約

一次審查拆成兩條互不相干的軸，各自審、各自報告（契約借自 two-axis-review playbook，見文末來源）：

- **Standard 軸（寫得對不對）**：diff 內部品質——對 team-rules 逐類（CORE／CODE／TEST／SEC／LEGACY／NAME）以規則編號走查。程序：[`references/standard-axis.md`](references/standard-axis.md)。
- **Spec 軸（做得對不對）**：diff 對外的達成度——把票拆成逐條接受條件，對 diff 逐條驗收（缺／多／錯）。程序：[`references/spec-axis.md`](references/spec-axis.md)。

鐵則：

1. 兩軸**平行、獨立**執行——各自在看不到對方結論的 context 裡跑；一軸的結論不得餵給另一軸。
2. 聚合**不合併、不重排序、不跨軸挑贏家**——兩份 verdict 原文並列呈報；一軸的乾淨會遮蔽另一軸的出軌。
3. **兩軸獨立命中同一位置＝高訊號事件**：聚合者除並列呈報外，必須對該位置做一次**合軸加驗**——把 Spec 軸的目標套到 Standard 軸指出的機制上，重問「這條路徑的目的還達成嗎」——加驗結論單獨列為聚合報告的第三段，**不改動兩軸原文**（這是對交會點的加驗，不是跨軸重排名）。

## 2. 執行形態

- 有委派能力時：兩軸**各派一個獨立子代理**（能力需求：唯讀 shell＋檔案讀取＋搜尋），**同一則訊息一次派出**，互不見對方 context。子代理 prompt 只需要：本檔路徑＋軸別＋素材（repo 路徑、diff 錨點、票全文——spec 軸）。
- 無委派能力時：先跑完一軸、把 verdict 落地（寫入暫存或貼進報告），再跑另一軸；過程中不回頭修改前一軸的結論。
- **輸入先驗後派**：ref 解不出、diff 空、票不存在——在派工前擋下，直接回 `status: BLOCKED`（缺什麼寫什麼），不要讓兩個平行審查各自撞牆一次。無票（test／chore 類）→ 只跑 Standard 軸，不派 Spec 軸。

## 3. verdict 與 status 契約（兩軸共用）

**status 判定**（每軸各自出一個 status；聚合者並列兩個 status，不合併）：

- `PASS`：無 finding，或僅有建議級 finding（已按分級標註）。
- `FAIL`：至少一個 **CONFIRMED** 的必要級（或條件成立之涉及時級）規則違反；或 Spec 軸任一接受條件不過。
- `BLOCKED`：素材缺件無法完成審查（票缺失、diff 空、ref 解不出、路徑不存在）。BLOCKED 時**只回報缺什麼**——不臨時發明政策、不降級標準、不代作者補件、不猜。保留 PLAUSIBLE 的必要級嫌疑不自動構成 FAIL，但必須列入 Limitations 作為待證事項呈報。

**回報格式**：

```
status: <PASS|FAIL|BLOCKED>
reviewer: <standard|spec>
target: <repo 路徑＠diff 錨點，或票號>

## Scope
（審了什麼：diff 範圍、票的條件數、走查的規則類別）

## Checks
（做了哪些取證：跑過的唯讀指令、讀過的檔案）

## Findings
（每條一行起：`檔案:行號`＋規則編號或票條編號＋一句缺陷＋具體失效情境
（什麼輸入→什麼錯誤結果）＋severity＋CONFIRMED／PLAUSIBLE；按嚴重度排序。
尾行：共 N 個 finding，其中 M 個 CONFIRMED。
無 finding 時：回報「無 finding」＋檢查過哪些面向。）

## Limitations
（查不到的部分、不適用的規則與原因、保留 PLAUSIBLE 的證據缺口）
```

**收工必做——report 檔（machine-readable status 出口，mounting-aware）**：完整回報
（首行＝status 行，即上方格式全文）的落地方式依 mounting 而定：

- **可寫檔的 mounting**（如 pane／頂層 session，有檔案寫入能力）：把完整回報寫入
  `${AGENT_STATE_HOME:-$HOME/.agent-state}/team-kit/reports/reviewer/<任務識別碼>-<UTC ts>.md`
  （`<UTC ts>` 例：`date -u +%Y%m%dT%H%M%SZ`；目錄先建）。任務識別碼取自派工 prompt
  （兩軸請由 dispatcher 給不同識別碼，如 `<票號>-standard`／`<票號>-spec`）。
- **subagent mounting（唯讀閘門）**：工具集無寫檔、Bash 被 git-only 閘門限制，
  report 寫檔**結構性不可行**——這是唯讀保證的代價，不是缺陷。此時不嘗試繞過閘門：
  完整回報以最終訊息交出（subagent 通道的最終訊息會由 dispatcher 原文代寫成 report 檔），
  並在 Limitations 註明「report 檔未自寫（唯讀閘門 mounting）」。
- 兩種 mounting 共同點：首行 status 契約不變；寫檔（或代寫）失敗不阻止收工，
  但必須在 Limitations 列出。

**severity 判準**：評級前必答一題——**這條路徑存在的目的，在 finding 成立時還達成嗎？** 靜默擊敗改動自身目的的缺陷＝Major，即使不崩潰、不損毀資料；「不崩潰」不是 low 的理由。

**CONFIRMED／PLAUSIBLE 紀律**：hinge 在「可能／或許」的 finding **不得直接交卷**——先在 repo 內找具體證據做一次值 trace（diff 上下文、fixtures、既有資料、日誌），把它釘成 CONFIRMED 或排除；真的找不到證據才保留 PLAUSIBLE，並在 Limitations 註明**缺哪個證據**。一次具體 trace 的成本遠低於漏報一個 Major。

**改善建議不冒充必要規範**：建議級規則（team-rules 分級＝建議）的 finding 必須標「建議」字樣與分級，附具體影響（耦合、維護成本、失敗情境），不得寫成「必須／不得」的規範口吻；只有必要級（或條件成立的涉及時級）違反構成 FAIL。規則沒要求、依個人偏好的重寫意見不提出。

## 4. 取證紀律

- **自跑取證，不以作者清單代替**：diff 內容以自跑的唯讀 git 指令為準（status／diff／log／show）；作者回報的檔案清單與「已測試」聲明只是線索——每條 finding 都要對到自己取得的證據，不是對到作者的敘述。
- 引用外部名稱或分類時沿 team-rules 的查證標記法（VERIFY-01）。
- 不確定的事實標「未確認」，不編造；禁止印象式評論（「品質不錯」「建議加強錯誤處理」）。

## 5. 對外留言：人類閘＋ledger

對外留言（票上 comment、PR 回覆等）**對外可見且不可撤回**；重跑審查是恢復常態，重貼是事故。任何對外留言：

1. **人類閘**：草稿（對象＋全文）先列給使用者，**明確說送出才貼**。審查報告本身不需要閘——只有對外寫入需要。
2. **ledger 防重貼**（模式借自 two-axis-review §7）：`$AGENT_STATE_HOME`（未設定時 `~/.agent-state`）/reviewer/`<target>.jsonl`（target＝票號或審查目標識別），append-only、一行一則、不改寫既有行：

   ```json
   {"ts":"<UTC ISO8601>","target":"<票號或審查目標>","hash":"<留言全文 sha256 前 12 碼>","summary":"<≤60 字摘要>"}
   ```

   三步順序不可換：(a) 貼前查 ledger 的 target——已記錄即跳過，並在報告寫「已於 `<ts>` 留言過」；target 命中但 hash 不同（結論後來改了）→ 停下來問使用者，不自行再貼。(b) 人類核准後貼。(c) 貼完立刻 append（hash：`printf '%s' "<全文>" | shasum -a 256 | cut -c1-12`）。

## 6. 跨 harness mounting

本檔與 `references/` 全部以**能力描述**表達工具（唯讀 shell、檔案讀取、搜尋、委派子代理），不寫死任何 harness 專屬工具名——其他 harness 可直接把本目錄當規則檔載入。各 harness 的唯讀保證與掛載差異（Claude Code／VS Code Local／Codex）見 [`references/mounting.md`](references/mounting.md)。

## 來源

- 兩軸拆分、聚合不合併、高訊號合軸、ledger 三步：契約借自 two-axis-review playbook（本 repo 的 two-axis-review plugin），借契約不抄全文。
- 取證紀律（自跑 git 取證、不以作者清單代替；BLOCKED 不臨時發明政策）：借自 HWDC code-review skill 的可攜部分。
- 規範依據：team-rules（§0 的相對路徑引用）。
