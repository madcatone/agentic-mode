Standards 軸共 3 個 finding：0 個 CONFIRMED／3 個 PLAUSIBLE／1 個 pre-existing
Spec 軸共 4 個 finding：0 個 CONFIRMED／4 個 PLAUSIBLE／1 個 pre-existing

# Two-Axis Review — TICKET-331「done state lost between runs」

## 審查設定

- **定錨**：base 樹 = `tests/review-evals/fixtures/todo-review/{todo,parse,store,commands}.py`；受審變更 = `change.patch`（已驗證可乾淨套用、非空）。票 = `TICKET.md`（bug-fix 類）。本地正典 = `.dev-notes/CODE-REVIEW.md`（查找鏈第一位命中，Standards 軸以它為主清單）。
- **取證**：base＋patch 已套至 `/tmp/review-eval-smoke/tree` 實跑（§4 值 trace），以下每個失效情境均附實際輸出。
- **深度分級（§9）**：Standard——小型 CLI 的 bug-fix，blast radius 為本機任務狀態，非付費／認證／遷移／CI 區域；bug-fix 類故 root-cause 查核必做（見 Spec 軸）。證據標準未降級。
- **verdict 上限說明**：單人環境、無可用獨立複核者——依 §4「CONFIRMED 須他驗」，所有 finding 的 verdict 上限為 PLAUSIBLE（X=0）。本案各 finding 均已有實跑重現證據，缺的只是他驗；升級條件一律為「由 fresh-context verifier 對照下列重現指令重跑並同意」。
- **§7**：票為 fixture 文件、無外部票務系統，本審查無任何對外留言，ledger 不適用。

---

# Standards 軸（寫得對不對）

Standards 軸共 3 個 finding：0 個 CONFIRMED／3 個 PLAUSIBLE／1 個 pre-existing

主清單 = `.dev-notes/CODE-REVIEW.md`（R1 單一儲存、R2 錯誤訊息格式、三個敏感區的「失敗長什麼樣」）。

### S1 [PLAUSIBLE] [Major] [introduced] — 違反 R1：新增 `done.log` 第二持久儲存

- **位置**：`commands.py:12-13`（`_DONE_LOG` 路徑）、`commands.py:38-41`（`append_done_id`）、`commands.py:59-65`（`cmd_list` 改讀 side log）。
- **缺陷**：任務的 done 狀態改存於 `tasks.json` 以外的 side file，直接違反正典 R1「Persistent task state lives in `tasks.json` and nowhere else. Do not add side files, shadow stores, or a second source of truth」；`store.py:1-4` 模組 docstring「The store is the single source of truth for task state」同遭推翻。
- **失效情境（實跑，D 組）**：`add "x"` → `done 1` → `rm 1` → `add "y"`（取得重用 id 1）→ `todo list` **輸出為空**（新任務 y 被當成 done 隱藏）、`todo list --all` 輸出 `[x] 1 y`——一個從未 done 的新任務被顯示為 done。這正是正典 Output 區定義的失敗樣貌：「the listing prints a task under the wrong state」。
- **附註**：`todo.py:3` docstring 同一批改成「state lives in tasks.json between runs」，與 done 狀態實際存在 `done.log` 的事實不符——改動自己寫下的宣稱即不成立。
- **升級條件**：fresh-context verifier 重跑 D 組重現（附錄）並同意。

### S2 [PLAUSIBLE] [Minor] [introduced] — 違反 R2：`done.log` 內容異常時 traceback 直達終端

- **位置**：`commands.py:35`（`{int(line) for line in fh.read().split() if line}`）。
- **缺陷**：`load_done_ids` 對 side log 內容做 `int()` 無任何防護，非數字內容使 `list` 直接拋 ValueError traceback，違反 R2「Tracebacks reaching the terminal are a violation」。
- **失效情境（實跑，E 組）**：`printf 'oops\n' > done.log && todo list` → 輸出完整 traceback（`ValueError: invalid literal for int() with base 10: 'oops'`，起自 `commands.py:35`），exit 1。
- **升級條件**：fresh-context verifier 重跑 E 組重現並同意。

### S3 [PLAUSIBLE] [Minor] [pre-existing] — `load()` 棄置已存 id，重啟後任務顯示在錯誤 id 上

- **位置**：`store.py:36`（`return [Task(i, row["title"]) for i, row in enumerate(rows, start=1)]`）。
- **缺陷**：`save()` 明明把 id 寫進 `tasks.json`，`load()` 卻用 `enumerate` 按位置重編，落在正典 Output 區失敗樣貌：「prints a task under the wrong id」。本 diff 未觸及 `store.py`。
- **失效情境（實跑，C 組）**：`add a,b,c`（存檔含 id 1,2,3）→ `rm 2`（存檔含 id 1,3）→ 重啟後 `list` 顯示 `[ ] 2 c`——c 在 add 時取得且已存檔的 id 3 憑空變成 2。
- **處置建議**：既有碼缺陷，照報、不擋 merge、不算作者失誤，建議另開票——但請併讀 Spec 軸 P3：本票 AC3 明列 id 穩定為驗收條件，故對本票而言它在範圍內（見合軸檢查）。
- **升級條件**：fresh-context verifier 重跑 C 組重現並同意。

---

# Spec 軸（做得對不對）

Spec 軸共 4 個 finding：0 個 CONFIRMED／4 個 PLAUSIBLE／1 個 pre-existing

## AC 逐條核對（均實跑）

| AC | 結果 | 證據 |
|---|---|---|
| AC1 done 跨行程存活 | **未達成** | 單一任務路徑通過（A 組：`[x] 1 write report`）；但標記第二個任務即抹掉第一個（B 組）→ P1 |
| AC2 隱藏 done／`--all` 帶 `[x]` | 達成（happy path） | A4 空輸出、A3 `[x] 1`。例外：id 重用時新任務被錯標 `[x]`／錯誤隱藏（D 組，機制屬 Standards S1，見合軸檢查） |
| AC3 id 跨 save/load 穩定 | **未達成** | C 組：rm 後重啟 id 重編、`done 3` 報 `error: unknown task id 3` → P3 |
| AC4 unknown id 錯誤訊息、exit 1、無 traceback | 達成 | A5：`error: unknown task id 42`、exit=1、無 traceback |

### P1 [PLAUSIBLE] [Major] [introduced] — AC1 擊敗：`append_done_id` 用 `"w"` 模式覆寫，第二個 done 抹掉第一個

- **位置**：`commands.py:40`（`open(_DONE_LOG, "w", ...)`——函式名稱叫 append、行為是 truncate）。
- **缺陷**：每次 `done` 以 `"w"` 開檔，整檔只剩最後一個 id；`load_done_ids` 因此至多回傳一個 id。
- **失效情境（實跑，B 組）**：`add "a"`、`add "b"` → `done 1` → `done 2` → `done.log` 內容只剩 `2` → `todo list --all` 輸出：

  ```
  [ ] 1 a
  [x] 2 b
  ```

  任務 1 的 done 標記跨行程丟失——**票面描述的原症狀原封不動重現**，只是現在需要兩個任務才觸發。此路徑的目的（修好 done 持久化）在 N≥2 時靜默失敗＝goal-defeat，故 Major。
- **升級條件**：fresh-context verifier 重跑 B 組重現並同意。

### P2 [PLAUSIBLE] [Major] [introduced] — root-cause 查核（§3）：成因在 `store.save/load` 序列化層，變更未指認、以 side log 繞過

- **位置**：成因在 `store.py:41`（`save()` 的 rows 只寫 `id`/`title`，**`done` 欄位從未序列化**）與 `store.py:36`（`load()` 丟棄已存 id 與 done）；本變更未觸及 `store.py`，改在 `commands.py:38-41` 另建 side log 壓症狀。
- **查核結論**：**未指認 root cause**。實跑 G 組釘死成因——base 樹上 `done 1` 後 `tasks.json` 內容為 `[{"id": 1, "title": "write report"}]`，`done` 欄位根本沒被寫入；亦即票的症狀不是「list 讀錯」，是序列化層從不保存該欄位。修法若對準成因（`save` 寫入 `done`、`load` 還原 `id`＋`done`），AC1/AC3 同時解，且不需要 side log。現修法繞過成因另立第二真值來源，該 workaround 自身又壞（P1）且違 R1（S1）——成因未動，同型缺陷（任何未進 `done.log` 的狀態仍會丟）會再發。
- **要求**：補指認成因並對準 `store.save/load` 修（要求說清成因，不是要求保留現有修法）。
- **升級條件**：fresh-context verifier 重跑 G 組重現（base 樹 `done` 欄位缺席於 `tasks.json`）並同意成因判定。

### P3 [PLAUSIBLE] [Major] [pre-existing] — AC3 未達成：`load()` 重編 id，任務無法保住 add 時取得的 id

- **位置**：`store.py:36`（缺陷碼，本 diff 之前即存在、本次未修）。
- **缺陷**：AC3 明文要求「a task keeps the id it was assigned at `add` time, across restarts and `rm` of other tasks」；`load()` 按 `enumerate` 位置重編，`rm` 中間任務後其後任務 id 全體前移。
- **失效情境（實跑，C 組）**：`add a,b,c` → `rm 2` → 重啟 `list` 顯示 c 為 id 2；對 c 的原 id 下指令 `done 3` 得 `error: unknown task id 3`、exit 1——使用者再也無法用 add 時的 id 標記 c。
- **標記說明**：缺陷碼屬 pre-existing；但 AC3 是本票驗收條件，「缺」（票要求而未做）屬本變更的交付缺口，不適用「pre-existing 另開票即可」的預設處置——完成本票需一併修 `store.py:36`（與 P2 同一處修法可覆蓋）。
- **升級條件**：fresh-context verifier 重跑 C 組重現並同意。

### P4 [PLAUSIBLE] [Minor] [introduced] — scope creep：`add` 新增同題名拒絕，票未要求

- **位置**：`commands.py:19-22`。
- **缺陷**：diff 加入「同 title 已存在即 `error: task already exists`、exit 1」的限制；TICKET-331 四條 AC 與症狀均與重複題名無關——屬 §3「多」（票沒要求的行為）。
- **失效情境（實跑，F 組）**：`add "milk"` 兩次——原先兩次都成功的操作，現在第二次得 `error: task already exists`、exit 1。清單類工具同題名任務是正當使用（兩家店都要買牛奶）；疊加 AC2 把 done 隱藏後，plain `list` 看不到已 done 的同題名任務，使用者會以為能再 add，卻被擋。
- **升級條件**：fresh-context verifier 重跑 F 組重現並同意。

---

# 合軸檢查（§5：兩軸獨立命中同一位置＝高訊號事件）

1. **`commands.py:38-41`（`append_done_id`）**——Spec P1（AC1 擊敗）與 Standards S1（R1 side store／Persistence 區「loses task state across a run boundary」）獨立命中。合軸重問 goal-defeat：票的目標（done 跨行程存活）套上此機制（`"w"` 單值覆寫＋side file），N≥2 必敗、id 重用時錯標新任務——合軸結論支撐兩軸各自的 Major 判定。
2. **`store.py:36`（`load()` 重編 id）**——Spec P3（AC3）與 Standards S3（Output 區 wrong-id 顯示）獨立命中。合軸結論：兩個失效共用同一修法（`load()` 讀回已存 `id` 與 `done`），且該修法同時是 P2 指認的 root-cause 修——一處修正可同時消解 P2/P3/S3，反證 side-log 路線是繞道。

# 附錄：重現指令（於套用 patch 後的樹根目錄執行；每組前 `rm -f tasks.json done.log`）

- A 組（AC1 單例／AC2／AC4）：`python3 todo.py add "write report" && python3 todo.py done 1 && python3 todo.py list --all`（得 `[x] 1 write report`）；`python3 todo.py done 42; echo $?`（得錯誤訊息與 1）。
- B 組（P1）：`add "a"`、`add "b"`、`done 1`、`done 2` 後 `cat done.log`（只剩 `2`）、`list --all`（任務 1 為 `[ ]`）。
- C 組（P3/S3）：`add a,b,c`、`rm 2` 後重啟 `list`（c 顯示為 id 2）、`done 3`（`error: unknown task id 3`）。
- D 組（S1）：`add "x"`、`done 1`、`rm 1`、`add "y"`、`list`（空）、`list --all`（`[x] 1 y`）。
- E 組（S2）：`printf 'oops\n' > done.log && python3 todo.py list`（ValueError traceback）。
- F 組（P4）：`add "milk"` 兩次（第二次 exit 1）。
- G 組（P2，base 樹）：`add "write report"`、`done 1` 後 `cat tasks.json`（無 `done` 欄位）。

（本審查為靜態雙軸審查＋值 trace 取證；merge 前另關的 build/test 驗證不因此免除，§0.3。）
