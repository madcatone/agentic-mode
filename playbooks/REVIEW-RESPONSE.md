# Review Response — responding to code-review feedback (playbook)

> **English summary.** Discipline for the author receiving code-review feedback:
> verify every comment against the codebase before implementing, no sycophantic
> openers, and always push back with evidence. Treat each piece of feedback
> (including the ticket description) as an external signal to be checked, then
> decide to adopt, rebut, or ask.

**About this playbook.** This file is the canonical, harness-neutral version.
Any collaborator — human or agent — can read it directly as a rules file;
installation as an optional plugin is described under `adapters/`. **Local repo
rules take precedence over this playbook.**

被審者側的六步流程與措辭規則。目標：**不盲從、不諂媚、不硬拗**——每則回饋先查證，再採納或有據反駁。

**啟動規則（重進時的第一步，不可跳）**：動手前先讀 §8 的 ledger 檔。**ledger 已存在＝這個 MR 曾處理到一半**——先把已貼清單列出來、與 API 抓回的 thread 全集對帳，已貼的一律跳過，只處理剩下的。沒讀過 ledger 就不准貼任何 comment。

## 1. 六步（不可跳 VERIFY）

**READ**（全文讀完，不急著反應）→ **UNDERSTAND**（用自己的話重述需求，重述不出來就直接問）→ **VERIFY**（對 codebase 查證，見 §3）→ **EVALUATE**（對**這個** repo、這個 stack 技術上成立嗎）→ **RESPOND**（技術性回覆或有據反駁）→ **IMPLEMENT**（一次一項、逐項測）。

先討好會誘導自己跳過 VERIFY 直接實作——所以措辭規則（§4）和流程綁在一起。

## 2. 信任分級

| 回饋來源 | 態度 |
|---|---|
| ticket／票面描述 | **視同外部回饋**——症狀常指錯層，**查證後才動** |
| reviewer 留言 | 查證後採納，或**有據反駁** |
| maintainer 既定架構決策 | 回饋與之衝突時，**先報告討論**——不默默照做，也不默默不做 |

## 3. VERIFY 用什麼查（本地儀器）

- repo 的知識庫（若有維護）：查對應 module 頁與 triage 知識。
- repo 的審查正典／pitfalls：`.dev-notes/CODE-REVIEW.md`、`AGENTS.md` 的 pitfalls/triage 章節。
- 單檔測試：只跑相關檔（如 `npm run test <File>.test.ts` 或該 repo 的等價指令）——別整套。
- raw diff 與該檔的 `git log` 史——看這行是誰、為什麼、何時加的。
- **查不動就明說**：「無法驗證 X，需要〔儀器／權限〕——要我〔查／問／先做哪個〕？」標注限制永遠優於帶著不確定硬做。

## 4. 回應措辭

**禁**：「You're absolutely right!」「Great point!」「Thanks for catching that!」——**空泛的**感謝與討好性開場。判準是**有無綁定具體內容**：綁定了具體問題與修正位置的簡短肯定**不在禁列**。

**用**：重述需求確認理解／直接動手讓 code 說話／「Fixed: <改了什麼>」／「Good catch — <具體問題>，fixed in <位置>」。判準始終是**綁不綁具體內容**——泛泛的「你說得對」誘導自己跳過查證，指名問題與位置的肯定則是有效溝通。

**反駁後發現自己錯了**：事實陳述並前進——「查了 X，你是對的；我原判斷錯在 Y，修正中。」**不寫長篇道歉、不辯解**當初為何反駁——道歉的篇幅不會讓修正更正確，只會稀釋掉「已修好」這件事。

## 5. 何時反駁（一律帶證據）

時機：建議會**壞既有功能**／reviewer **缺完整 context**／**YAGNI**（先 grep 實際用量，沒人呼叫就提議刪除而非「好好實作」）／技術上**不適用本 stack**／有 **legacy 相容**原因／**與既定架構衝突**。

**帶證據的第三種答案**（教案，來自某真實 repo 的 pitfalls 記載）——reviewer 說「用 `replaceAll`，這是標準 API」：

- ❌ 照做（沒查目標執行環境的引擎相容性）；❌ 拒絕（「本引擎不支援」——只對一半）。
- ✅ 「目標執行環境的原生 JS 引擎（某嵌入式 engine）無此 builtin，但建置管線的 preset-env＋polyfill 已補上、`src/` 已有多處在用——**目前安全**；但若有人移除該 polyfill 設定會整批壞（repo 的 pitfalls 檔有記載）。」

第三種答案＝不是照做也不是拒絕，而是**帶查證結果**把條件與風險一次講清楚。核心動作是**目標執行環境相容性查證**：先確認你的 stack 實際跑在什麼引擎/runtime 上，再判定某 API 能不能用。

## 6. 多項回饋

- **任何一項不清楚 → 全部先停、先問。** 項目之間可能相關，部分理解＝錯誤實作。（「懂 1,2,3,6、不懂 4,5」的正確回應是**先問 4,5**，不是先做 1,2,3,6。）
- 實作順序：**blocking（壞掉／安全）→ 簡單修（typo／import）→ 複雜修（重構／邏輯）**——先讓 build/測試回綠，再處理耗時的那些。
- **每項修完各自跑測試，不批次**——批次測會讓你分不清哪項出的錯，一個 red 就要回頭拆是哪一項造成的。

## 7. 回覆位置

- **GitLab**：inline 討論回在**原 discussion thread**（`POST /projects/:id/merge_requests/:iid/discussions/:discussion_id/notes`），不開新的 top-level note——讓對話留在被討論的程式碼旁。
- **GitHub**：對應做法是**在該 review comment 的 thread 內 reply**，同樣不另開頂層 comment。
- 兩者**貼出前都必須走 §8**（人類閘 ＋ ledger 查核）。

## 8. 貼出前：人類閘 ＋ 已貼 ledger

對外 comment **不可逆、且 API 沒有唯一性約束**——重貼一次不會報錯，只會讓同一條 thread 多出一則一字不差的回覆，對所有 watcher 可見。

**人類閘（先草稿、後送出）**：所有回覆先產成草稿**一次列給使用者看**（每則標 `thread id ＋ 回覆全文`），**使用者明確說送出才 POST**。沒有這句話就停在草稿，不要邊寫邊貼。

**ledger 路徑**（放 repo 外、跨 session 可推導；`<host>` 與 `<project-path>` 取自 `git remote get-url origin`，路徑分隔的 `/` 換成 `-`）。狀態根目錄取 `AGENT_STATE_HOME`，未設定時預設 `~/.agent-state`——**一個環境只挑一次、之後不再改**，冪等性靠這個路徑穩定：

```
$AGENT_STATE_HOME/review-response/<host>--<project-path>--mr-<iid>.jsonl
例：~/.agent-state/review-response/gitlab.example.com--group-sub-proj--mr-412.jsonl
GitHub 用 --pr-<number>。
```

**推導指令**（照抄可跑；ssh 與 https remote 必須推出同一個檔名，冪等性靠這點，不要即興改寫）：

```sh
IID=412   # 換成本次的 MR iid；GitHub PR 填 PR number，並把下面的 mr- 改成 pr-
SLUG=$(git remote get-url origin | sed -E 's#^[A-Za-z0-9+.-]+://##; s#^[^@/]+@##; s#^([^/:]+):#\1/#; s#\.git$##; s#/+$##; s#/#--#; s#/#-#g')
LEDGER="${AGENT_STATE_HOME:-$HOME/.agent-state}"/review-response/"$SLUG"--mr-"$IID".jsonl
mkdir -p "$(dirname "$LEDGER")"; touch "$LEDGER"; echo "$LEDGER"
```

七個 sed 步驟依序是：去 scheme（`https://`／`ssh://`）、去 `user@`、scp 式 `host:group/…` 的第一個 `:` 換成 `/`、去尾綴 `.git`、去尾綴 `/`、第一個 `/` 換 `--`（切開 host 與 project-path）、其餘 `/` 換 `-`。**不支援帶 port 的 remote**（`https://host:8443/…` 會把 port 併進 slug，且同一 repo 的 ssh／https port 不同時會算出兩個檔名）——遇到就手動寫死 `SLUG`。

**格式**：一行一則 JSON，append-only，不改寫既有行：

```
{"ts":"2026-08-01T09:12:33Z","target":"<discussion_id>","hash":"<回覆全文 sha256 前 12 碼>","summary":"<≤60 字摘要>","note":"<API 回傳的 note id 或 url>"}
```

**每則回覆的三步，順序不可換**：

1. **貼前查 ledger**——`mkdir -p "$(dirname "$LEDGER")"; touch "$LEDGER"; grep -Fc '"target":"<discussion_id>"' "$LEDGER" || true`（`|| true` 不可省：grep 查無結果時印 `0` 但 exit 1，會被誤讀成指令失敗）。印出非 0 就**跳過這則**，並在收尾說明「已於 `<ts>` 貼過」。若 target 命中但 hash 不同（回覆內容後來改過）→ **停下來問使用者**要不要補貼，不要自行再貼一則。
2. **POST**（位置依 §7）。
3. **貼完立刻 append**（同一輪就寫，不要等整批做完）：
   `printf '%s\n' "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"target\":\"…\",\"hash\":\"…\",\"summary\":\"…\",\"note\":\"…\"}" >> "$LEDGER"`
   hash 算法：`printf '%s' "<回覆全文>" | shasum -a 256 | cut -c1-12`（Linux 用 `sha256sum`）。

**恢復情境（重進時怎麼走）**：第一步永遠是算出上面的 ledger 路徑並讀它，第二步才是抓 thread 全集對帳。「POST 成功但還沒 append」是唯一會漏記的窗口——所以這輪若是恢復（ledger 已存在且未處理完），對**尚未記錄**的 thread 在貼之前先 `GET .../discussions/:discussion_id`，看最後一則 note 是不是自己貼的同內容：是就補寫 ledger 並跳過，不要重貼。
