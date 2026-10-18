# Standard 軸程序——對 team-rules 逐類走查（寫得對不對）

> 輸入：repo 路徑、diff 錨點（base ref 或工作區）。輸出：SKILL.md §3 契約的 verdict（`reviewer: standard`）。
> 本檔只定義**程序與檢查重點**；規則本體一律以 [`team-rules`](../../../rules/team-rules.md) 為準，以規則編號引用，不在此重寫標準。

## 1. 定錨與取證（先做）

1. **驗錨點**：以 git rev-parse 確認 base ref 可解析；解不動 → `status: BLOCKED`（缺：可解析的 base ref）。
2. **取 diff**：已提交變更用 `git diff <base>`（merge-base 三點式優先）；未提交的工作區變更用 git status ＋ git diff。diff 空 → `status: BLOCKED`（缺：非空 diff）。
3. **取脈絡**：git log（commit 脈絡）、git show（單 commit 全文）、git blame（疑點歸屬——判斷問題是本次引入還是既有，這是 LEGACY-01 的分界線）。
4. **自跑取證，不以作者清單代替**（SKILL.md §4）：逐 hunk 讀 diff，必要檔案讀全文——finding 的行號與情境必須來自自己看過的內容。

## 2. 逐類走查（規則編號 → reviewer 檢查重點）

| 類別 | 規則 | reviewer 檢查重點 |
|---|---|---|
| CORE | CORE-01 | 程式行為是否來自未經確認的假設（無依據的魔法常數、自行假定的邊界）→ finding |
| | CORE-02 | diff 是否含任務未要求的功能／一次性抽象／未要求的可設定性 → 阻擋；寫法可簡化但不影響需求 → 建議 |
| | CORE-03 | diff 逐行對應本次任務或 finding——找不到依據的變更 → 阻擋；本次改動造成的不使用 import／變數／函式未移除 → finding |
| | CORE-04 | 任務的接受條件是否有對應測試（與 TEST-01 同查） |
| CODE | CODE-01 | 變更是否限於核准範圍；公開契約與行為是否在未核准下改變 |
| | CODE-02（涉及時：I/O） | 條件成立才查：非同步阻塞、取消機制傳遞 |
| | CODE-03 | 吞例外、回報假成功、遺失原始錯誤資訊 |
| | CODE-04 | 可空值、邊界條件、資源釋放；生命週期不明的可變全域狀態 |
| | CODE-05（涉及時：共享狀態） | 並行安全主張是否有依據 |
| | CODE-06 | 日誌結構化與等級（機密欄位轉 SEC 類檢查） |
| | CODE-07 | 本次變更引入的新診斷；以抑制警告／關分析器換綠燈 |
| | CODE-08（建議） | 高影響重複／過深分支——附具體影響才提，不依偏好要求抽象化 |
| TEST | TEST-01 | 測試是否真的驗證需求——名稱與數量不是證據，逐 assertion 對接受條件 |
| | TEST-02 | 測試層次是否對應變更責任（單元／流程／整合） |
| | TEST-03 | 修缺陷是否有能重現原問題的回歸測試 |
| | TEST-04 | 測試可重現、隔離、有實質 assertion；無空白範本測試 |
| | TEST-05（涉及時：安全機制） | 是否停用防護機制換取測試通過 |
| | TEST-06 | 作者回報是否含 build／test 實跑輸出，且非零測試、無略過——reviewer 查證據存在與誠實，不代跑 |
| | TEST-07 | 是否以刪除／跳過／弱化測試消除 FAIL |
| SEC | SEC-01…SEC-13 | 只按本次變更及相關設定檢查——不存在的 SQL／檔案／外部呼叫不虛構 finding；涉及時級先判條件，不成立標「不適用」不是違規 |
| LEGACY | LEGACY-01 | 新增／修改的程式符合規範；既有問題記技術債提出，不要求擴大重構 |
| | LEGACY-02／LEGACY-03 | 作者回報的 BLOCKED 與例外是否如實記錄（規則編號、原因、影響、替代措施、後續） |
| NAME | NAME-03 | 程式與回報的領域用語是否與需求文件一致 |
| | NAME-05（建議） | 泛稱命名——僅當名稱無法表達責任時提具體替代 |

走查方式：逐類過表，每條規則要麼有 finding、要麼在 Limitations 記「不適用／已查無異常」；不跳類。「涉及時」規則的條件判斷（I/O？共享狀態？資料庫？…）寫進 Limitations，讓不適用有跡可查。

## 3. 分級處理（沿 team-rules 分級）

- **必要**：違反即 finding；CONFIRMED 後構成 `FAIL`。
- **建議**：finding 標「建議」，必須附具體影響；不構成 `FAIL`，不得寫成規範口吻（SKILL.md §3）。
- **涉及時**：先判條件成立與否——成立→同必要處理；不成立→Limitations 標「不適用」與原因，不是違規。

## 4. 輸出

照 SKILL.md §3 契約出 verdict：`reviewer: standard`；每條 finding 帶規則編號（如 `SEC-01`）；`Checks` 段列實際跑過的取證指令。
