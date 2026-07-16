---
name: two-axis-review
description: 雙軸 code review——Standards（寫得對不對）與 Spec（做得對不對）平行分審、不互相污染；當使用者要 review 一個 MR/PR/diff、說「two-axis review」「雙軸審查」「審這個 MR 對不對票」、或要對照 ticket 驗收實作時使用。多出「對票驗收（Spec 軸）」——把實作逐條核回 ticket 的要求。
---

# Two-Axis Review — dual-axis code review (playbook)

> **English summary.** Split one review into two axes that are audited and
> reported independently and never cross-contaminate: **Standards** (is the diff
> written right — quality, defect patterns, style) and **Spec** (does the diff
> meet the ticket). Every finding cites `file:line` plus a concrete failure
> scenario. If the repo has its own review canon, that is the Standards
> checklist; this playbook only adds the ticket-acceptance (Spec) axis.

**About this playbook.** This file is the canonical, harness-neutral version.
Any collaborator — human or agent — can read it directly as a rules file;
installation as an optional plugin is described under `adapters/`. **Local repo
rules (a review canon, a defect taxonomy) take precedence over this playbook.**

一次 review 拆成兩條互不相干的軸，各自審、各自報告：

- **Standards 軸（寫得對不對）**：程式碼品質、缺陷模式、風格慣例——diff 內部的正確性。
- **Spec 軸（做得對不對）**：實作有沒有滿足 ticket 要求——diff 對外的達成度。

若你的工具內建一個只審 diff 品質的 code-review 功能，它大致等於 Standards 軸；本 playbook 保留那條軸，並**多出 Spec 軸**——把實作對照票逐條驗收。要做完整「對票 review」時走兩軸；只想看 diff 品質時單審 Standards 軸即可。

## 0. 三條地基

1. **雙軸分離**：兩軸分開審、分開報告、**不合併排名、不跨軸挑贏家**——一軸的乾淨會遮蔽另一軸的出軌。經典失效：一支標題「update release」的 MR 在 reformat 噪音裡拿掉了關鍵比對欄位，格式全對、行為出軌。
2. **證據優先**：每個 finding 都要能定位（`檔案:行號`）與重現（具體失效情境）。印象式評論（「品質不錯」「建議加強錯誤處理」）視同沒審。
3. **不取代驗證**：本 playbook 是**靜態審查**；`build / test / lint` 實跑是另一關，兩關都過才算完成。不要用「我審過了」代替「我跑過了」。

## 1. 定錨（開審前先做，兩軸共用）

- **固定點**＝MR 的 target branch（依 repo，如 `dev/row`、`main`）。diff 用**三點式** `git diff <base>...HEAD`（對 merge-base 比較），避免把 base 分支的無關改動也算進來。
- **票號從 commit 訊息解析**——repo 若有 commit-msg hook 強制 `fix TICKET-123: ...` 格式最可靠；沒有的話從 branch 名與 MR 描述找。票號 prefix 因 repo 而異。
- **ref 驗證先於派工**：先確認 base/HEAD 可解析（`git rev-parse`）、diff 非空。壞的定錨要在**這裡**失敗，而不是在兩個平行 agent 裡各自失敗一次。

## 2. Standards 軸（寫得對不對）

**本地正典優先——先找這個 repo 自己的審查文件當主 checklist：**

1. 依序找：`.dev-notes/CODE-REVIEW.md` → repo 根的 `CODE-REVIEW.md` → `AGENTS.md` 的 pitfalls／triage 章節 → `CONTRIBUTING.md`。找到就以它為 Standards 軸的主清單——repo 自己的實證缺陷表命中率遠高於任何通用 smell 清單。若 repo 維護了自己的缺陷分類（例如一張按類別列出的實證缺陷表：條件遮蔽、狀態作用域、快取旗標、非同步時序、空值集合、平台引擎、註冊完整性、guard 語意、明文憑證……），**先讀它、以它為準**。
2. **找不到本地正典才用下面的通用 fallback。** 不要用通用清單覆蓋本地正典。

**通用 fallback（無本地審查文件時）——只列三項有訊號的 smell：**

- **Duplicated Code**：平行路徑同型邏輯——同一個守衛缺陷常同時在多條相似路徑，只修一條漏其餘。
- **Repeated Switches（僅限新增的）**：diff 新增的重複 switch/if-else；既有的巨型分派表若是該 repo 既定架構，**不標**。
- **Speculative Generality**：票沒要求的抽象、hook、參數化。

其餘通用 smell（Feature Envy、Middle Man、Message Chains…）在多數應用型 repo **噪音大於訊號，不納入**——硬套只會淹沒真正的 finding。ESLint／SonarQube 等 tooling 已強制的規則**跳過**，不用人肉重審；把人的注意力留給 tooling 抓不到的語意缺陷。

## 3. Spec 軸（做得對不對）

**來源與信任規則：**

1. ticket 用 fetch 工具抓，**必含 comments**——關鍵 log 通常在 comments 不在附件；要下載大附件（log/video）前先讀 comments 決定值不值得。
2. **票面只是線索，不是地面真相**：症狀常指錯層，`label`／`component` 會誤導（實例：標「輸出格式」的票，真缺陷在上游資料 mapping；標「音訊」的票，實際修在對話狀態層）。裁決一律以 **diff 與 raw 證據**為準；有實證的 repo 裡「真缺陷票近半症狀指錯層」不是特例而是常態。
3. **無對應票**（test/chore/release 類）→ Spec 軸回報「no spec」，只跑 Standards 軸——但 release/merge 類要加抓夾帶（見下）。

**審什麼——缺／多／錯三類：**

- **缺**：票要求的行為沒做或做一半。特別盯「**平行路徑只修了一條**」——修一條漏兩條等於沒修完。
- **多（scope creep）**：diff 裡有票沒要求的行為。**release/merge 載體 MR 是重災區**——逐 hunk 讀 diff，不看標題。
- **錯**：看起來實作了但語意不對——對照票的重現步驟與期望行為逐條核。

## 4. Finding 格式（DoD）

每條 finding：**`檔案:行號` ＋ 一句缺陷描述 ＋ 具體失效情境（什麼輸入 → 什麼錯誤結果）＋ severity ＋ `CONFIRMED`／`PLAUSIBLE` 標記**。報告結尾一行：**「共 N 個 finding，其中 M 個 CONFIRMED」**。找不到問題就回報「無 finding」＋檢查過哪些面向。

**severity 判準**：severity 評級前必答一題——**這條路徑存在的目的，在 finding 成立時還達成嗎？** 靜默擊敗改動自身目的的缺陷（例：修復的核心路徑實際 no-op）＝ **Major**，即使不崩潰、不損毀資料——「不崩潰」不是「low」的理由。

**CONFIRMED／PLAUSIBLE 釘死**：hinge 在「可能／或許」上的 finding **不得直接交卷**——先在 repo 裡找具體證據做一次值的 trace（UT fixtures／mocks，grep 症狀關鍵字如錯誤碼；票附件 log；raw payload），把它釘成 CONFIRMED 或排除。一次具體 trace 的成本遠低於漏報一個 Major；真的找不到證據才保留 PLAUSIBLE，且必須註明**缺哪個證據**。（實例：「id 可能為空」用 repo 內建的錯誤碼 fixture 走一遍即變「恆為空」。）

- ✅ 正例：`lookup.ts:42 [CONFIRMED] 查表 key 大小寫不符——來源 enum 成員為大寫、查表用小寫 key，當輸入含大寫字面值時查落空、fallback 直接把原字串輸出到使用者可見層。`
- ❌ 反例：「整體程式碼品質不錯，建議加強錯誤處理。」——不可定位、不可重現，視同沒審。

## 5. 執行形態

- 兩軸**各派一個獨立 agent 平行審**（**同一則訊息**一次派出、互不見對方 context）。
- 主對話**聚合**兩份報告——**不合併、不重排、不跨軸挑贏家**，兩份並列呈報。
- **兩軸獨立命中同一位置＝高訊號事件**：聚合者不得只並列呈報，必須對該位置做**第三次合軸檢查**——把 Spec 軸的目標套到 Standards 軸的機制上，重問 §4 那題（goal-defeat），必要時派一個 mini verify。這不是跨軸重排名（不合併、不重排的原則不變），是對交會點的加驗。
- 任一軸的輸入壞掉（票抓不到、diff 空、ref 解不出）在**派工前**就擋下，不要讓 agent 各自撞牆。

## 6. 回流（審查產出不是終點）

- 審出**重複出現（≥2 次）的新模式** → 蒸餾進 repo 的知識庫（若有），落對應 module 頁；跨多 MR 成熟後提案進 repo 的審查正典（`CODE-REVIEW.md`／`AGENTS.md` pitfalls）。
- Spec 軸審出「**票面指錯層**」→ 在票上留言記錄實際層別，餵未來 triage 統計。
