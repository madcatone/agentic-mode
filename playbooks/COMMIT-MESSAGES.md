# Commit Messages — team convention (playbook)

> **English summary.** A Conventional-Commits variant for writing commit
> messages: a type table (with explicit build / ci / chore adjudications), an
> optional ticket appended between the type and the colon (on demand, never
> mandatory), and scope rules. A repository's own commit-msg hook or agent rules
> file always wins over this playbook.

**About this playbook.** This file is the canonical, harness-neutral version of
the convention. Any collaborator — human or agent — can read it directly as a
rules file; installation as an optional plugin is described under `adapters/`.
**Local repo policy (a commit-msg hook, an `AGENTS.md` rule) always takes
precedence over this playbook** — this playbook is the default, not the law.

格式：

```
<type>[ <TICKET>]: <description>

[optional body]

[optional footer(s)]
```

## 先查本地規則（優先於本準則）

repo 若有 commit-msg hook（常見於 `hooks/` 目錄）或 `AGENTS.md` 內的 commit 規範，一律以 repo 為準。本 playbook 是預設值，本地政策覆寫它。

### Local policy（可覆寫段——示範一個假想團隊的政策）

團隊常在 hook 裡加自己的約束。舉例（佔位示範，非硬規則）：某團隊的 hook 強制 `feat`/`fix`/`docs`/`refactor`/`perf` 必附票號、prefix 限 `PROJ-`、不接受括號 scope、不接受 `ops` type、另接受 `release` type。遇到這類本地政策，先讀 repo 的 hook 與 rules 檔，以它為準，再套用本 playbook 的其餘部分。

## Type（擇一）

| type | 用於 |
|---|---|
| `feat` | 新增功能 |
| `fix` | 修 bug |
| `refactor` | 重寫／重組程式碼，不修 bug 也不加功能 |
| `perf` | 以效能為目的的特殊 refactor |
| `test` | 補缺的測試或修正既有測試 |
| `docs` | 純文件（README、guides） |
| `style` | 純格式：空白、分號等，不改語意 |
| `build` | build 系統、建置工具、依賴、專案版本（**依賴更新歸 build，不歸 chore**） |
| `ci` | CI 設定檔（**只有 CI 設定歸 ci，不歸 build**——兩型不重疊） |
| `ops` | 維運元件：基礎設施、部署、備份、還原 |
| `chore` | 以上皆非且不動 src/test 檔（例：更新 `.gitignore`） |
| `revert` | 撤銷先前的 commit |

## 票號（按需，不強制）

- 改動對應到追蹤中的票就附上：`fix PROJ-123: Correct teardown on sync event`
- 位置在 type 與冒號之間，空格連接，不用括號。
- 沒有對應票（順手修 typo、工具腳本、文件）就省略：`docs: Fix stale link in README`
- repo 的 hook 若強制票號（見上節），以 hook 為準。

## Scope

- 只在「一個明顯的單字」能命名觸及範圍時加（`auth`、`export`、`ci`）；想不出單字就省略。
- 票號與 scope 只擇一，優先票號。
- subject 超過 50 字元時先捨 scope 保描述。
- 部分 repo 的 hook 不接受括號 scope——先查本地規則。

## Subject

- 全長 ≤50 字元——含 type、票號、scope 在內；票號吃掉字元時精簡描述，不省票號。
- type 小寫；描述（冒號後那段）首字大寫。
- 祈使句。自測：subject 應能接完「If applied, this commit will ___」。
- 結尾不加句點。

## Body

- 與 subject 之間空一行；每行 ≤72 字元換行。
- 寫 what 與 why——how 讓 diff 自己說。
- 判準：diff 本身看不出 why 才寫 body（例：「Node 16 已 EOL」）；看得出就整段省略。

## Footer

- 不加作者行（`Co-Authored-By`／`Signed-off-by`），除非使用者明確要求。
- 破壞性變更用 `BREAKING CHANGE: <說明>`。

## 範例

好：

```
fix PROJ-123: Prevent crash on missing config

The loader assumed config.json always exists and dereferenced the
parse result unconditionally. Return defaults instead so first-run
users are not forced to create the file manually.
```

```
build: Bump webpack to 5.90 for Node 20 support
```

壞（附一句原因）：

- `fixed the bug`（無 type、非祈使、未大寫）
- `feat(parser): Added new rule.`（過去式、句尾句點；且在有 hook 的 repo 括號 scope 會被拒）
- `chore: Update dependencies`（依賴更新應為 build）
