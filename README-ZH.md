# agentic-mode（繁體中文）

一套**文件契約**，讓任何協作者——不論是人還是 agent、用哪個工具、**沒有任何對話歷史**
——都能讀懂一個 repo。它是一組分層、互相交叉引用、以穩定 ID 串接的文件，外加一支
以 config 驅動的檢查器與 CI gate，用來防止這些文件與程式碼失去同步。

本 repo 是這套方法論的**正典（canonical source）**。下游拷貝（Claude Code plugin、
Devin IDE rule、vendor 進你自己 repo 的 subtree）都應該**從這裡同步**——見
[轉接層](#轉接層adapters)與[正典來源](#正典來源)。

> English version: [README.md](README.md)。本檔與英文版資訊等價。

## 為什麼

對話歷史不是耐久的載體。只要換一個協作者——不同的人、不同的 agent、新的 session
——所有只存在於對話裡的東西就消失了。團隊常用一份 `NOTES.md` 硬撐，把契約、指南、
狀態、流程全混在一起，直到沒人知道哪一段才是權威，然後它就腐爛了。

agentic-mode 用三個原則解決這件事（完整教義見
[`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md)）：

1. **分層、不重疊的文件。** 每個檔案只做一件事；每個事實只有一個正典所在地，用交叉
   引用而非在多處各自成為獨立權威。
2. **每個行為都有穩定 ID。** 需求以 `PREFIX-001` 編號；使用者指南、驗證區塊、commit、
   MR/PR 說明全都引用它。ID 是**串接鍵（join key）**，讓任何讀者不靠對話歷史就能在
   各層之間跳轉。
3. **append-only 的來歷 + 逐功能的完成證據。** iteration history 記錄一個改動**為何**
   落地（永不改寫）；validation 區塊記錄它**確實做完了**以及如何重新驗證。

契約擁有 **What**（repo 事實、行為契約）與 **Done**（驗收證據），但**絕不**規定
**How/Who**（你用哪個工具、model、如何派工）——後者留給實際做事的人，這正是契約能
在每一種 harness 之間保持可攜的原因。

## 快速開始

你只需要 Python 3（標準函式庫）與 git。唯一入口是 [`RUNBOOK.md`](RUNBOOK.md)：把任何
agent 指向它（「讀這個檔案並執行」），或你自己照著做。

### Bootstrap 一個新 repo

執行 `RUNBOOK.md` 的四階段協定：repo 掃描 + 10 題訪談（Phase A）、依相依順序逐一產生
分層文件且每個 gate 都通過（Phase B）、複製檢查器並佈線 CI（Phase C）、交接給自我運作
（Phase D）。成果是一個任何協作者都能冷啟動操作的 repo。

### Adopt 一個既有 repo

若 repo 已經有 `AGENTS.md`、`README`、或零散的 `docs/`，用 **Adopt mode**（也在
`RUNBOOK.md`）：盤點既有內容、**絕不覆寫**手寫文件、只補缺的分層、並調整 config 指向
真實檔案所在。Adopt 刻意保守——目標是連貫性與可強制性，不是重寫。

### 看它實際運作

[`examples/minimal-cli/`](examples/minimal-cli/) 是一個虛構小型 `todo` CLI 的完整、
可通過檢查的契約。對它跑 gate：

```bash
python3 checker/check_agentic_docs.py \
  --config examples/minimal-cli/agentic-mode/config.json \
  --root examples/minimal-cli
```

它會以每一項檢查全綠、exit `0` 結束。由上而下閱讀該範例的文件，就能完整看到一份填好的
契約。

## 檢查器

`checker/check_agentic_docs.py` 是純標準函式庫、config 驅動的 gate。所有專案特有的東西
（ID 前綴、文件路徑、雙語標題、entry points、指令規則、deny words、allowlist）都放在
外部的 `agentic-mode/config.json`——框架程式碼在各專案間完全不變。把它複製進 repo、
旁邊放一份 config、然後執行：

```bash
python3 scripts/check_agentic_docs.py --config agentic-mode/config.json
```

輸出格式為 `<file>:<line>: [<category>] <message>`，exit `0`（乾淨）、`1`（有 finding）、
`2`（config 壞掉／I/O 錯誤）。檢查類別：

| 類別 | 檢查什麼 |
| --- | --- |
| `id-continuity` | `PREFIX-NNN` ID 無跳號、無重複；surface/validation 引用的 ID 都有定義；雙語區塊共享相同 ID 集合。 |
| `iteration-continuity` | *(選用)* iteration history 的編號無跳號。 |
| `command-consistency` | 每條設定的指令字串逐字出現在每個該攜帶它的文件裡。 |
| `neutrality` | deny words、內建 harness deny 清單、非 allowlist 的 URL host，以及 *(選用)* IPv4 字面值／單機路徑。 |
| `line-limit` | 每檔行數上限（例如 `AGENTS.md`）。 |
| `entrypoint` | 宣告的 entry point 存在；`.py` 者可 byte-compile。 |
| `doc-presence` | 每個宣告的文件路徑都存在。 |

任何帶有 `agentic-gate: allow` 標記的行會被文字掃描略過，所以規則／規格文件可以刻意
引用壞例子。所有旋鈕見 [`checker/config.example.json`](checker/config.example.json)。

## Repo 地圖

| 路徑 | 是什麼 |
| --- | --- |
| [`RUNBOOK.md`](RUNBOOK.md) | 唯一可執行協定——bootstrap/adopt、Phase A–D、config schema、硬規則。從這裡開始。 |
| [`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md) | 教義：為何分層、ID 紀律、append-only 規則、優先序、adoption profiles。 |
| [`doctrine/FIELD-NOTES.md`](doctrine/FIELD-NOTES.md) | 來自原始專案、形塑了教義的實戰教訓。 |
| [`checker/`](checker/) | config 驅動的檢查器與一份註解過的範例 config。 |
| [`templates/`](templates/) | 每份產出文件的填空骨架 + CI 檔。 |
| [`adapters/`](adapters/) | harness 專屬的包裝（Claude Code skill、Devin IDE rule + review workflow）。 |
| [`examples/minimal-cli/`](examples/minimal-cli/) | 一個可通過檢查器的完整範例。 |
| [`AGENTS.md`](AGENTS.md) | 本 repo 自己的契約（吃自己的狗糧）。 |

## 轉接層（adapters）

核心（doctrine、RUNBOOK、templates、checker）是 **harness-neutral** 的——絕不指名任何
特定 agent 產品、model 或專有工具。harness 專屬的包裝只放在 [`adapters/`](adapters/)：

- [`adapters/claude-code/SKILL.md`](adapters/claude-code/SKILL.md)——把工具包裝成
  Claude Code skill。
- [`adapters/devin-ide/`](adapters/devin-ide/)——一份 Devin IDE rule 與一個 review
  workflow。

每個 adapter 都很薄：它指向根目錄的 `RUNBOOK.md`，並把路徑解析到 vendor 進來的核心。
要支援新 harness 就新增一個 adapter，不要 fork 教義。

## 正典來源

本 repo 是 agentic-mode 方法論的正典來源。當你把它 vendor 到下游（plugin、IDE rule、
subtree），請**從這裡同步**，不要手改 vendor 進來的 `doctrine/`、`templates/`、
`checker/`——一個永不回流的下游修改會變成無聲的漂移。若下游需要新能力，先在這裡加，
再重新同步。

## 授權

[MIT](LICENSE) — © agentic-mode contributors。
