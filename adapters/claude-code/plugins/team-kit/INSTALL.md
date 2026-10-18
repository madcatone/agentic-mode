# team-kit 安裝（INSTALL）

本 plugin 是 team-kit 的**正典來源**：四個角色 skill（observer／coder／reviewer／fortify）、
規範（`rules/team-rules.md`）、hook 腳本（`eng/`）、狀態面契約（`STATE-CONTRACT.md`）與
agent 定義**範本**（`agents/`）。個人目錄裡的安裝（例：`~/.claude/team-kit`）是本範本的
實例——升級方向一律「改這裡 → 重新安裝」，不逆向手改安裝目錄。

## 目錄結構

```text
team-kit/
├── .claude-plugin/plugin.json   # plugin manifest
├── STATE-CONTRACT.md            # 執行期狀態 artifact 的單一契約
├── INSTALL.md                   # 本檔
├── rules/team-rules.md          # 規範單一來源（以規則編號被各 skill 引用）
├── skills/
│   ├── observer/                # 純 dispatcher（含 references/herdr-contract.md）
│   ├── coder/                   # 實作 worker（verify 通過才收工）
│   ├── reviewer/                # 兩軸唯讀審查（含 references/ 三檔）
│   └── fortify/                 # 安全預檢（含 references/data-flow.md）
├── eng/                         # verify.sh、verify-on-stop.sh、reviewer-git-only.sh＋tests/
└── agents/                      # agent 定義「範本」——安裝時複製並替換佔位符
```

skill 之間的引用一律是**相對於 skill 目錄**的路徑（如 `../../rules/team-rules.md`），
因此安裝時必須**整棵樹一起帶**，目錄結構完整即處處可解析（見
`skills/reviewer/references/mounting.md`）。

## 佔位符

`agents/` 內的範本用兩個佔位符標示安裝位置：

| 佔位符 | 意義 |
|---|---|
| `<TEAM_KIT_DIR>` | kit 根目錄絕對路徑（其下有 `skills/`、`rules/`、`eng/`） |
| `<TEAM_KIT_ENG>` | `eng/` 目錄絕對路徑（即 `<TEAM_KIT_DIR>/eng`） |

## 安裝方式一：Claude Code plugin

1. 經 marketplace 安裝本 plugin（`/plugin install team-kit@agentic-mode`）——四個 skill
   由 plugin 機制載入（observer 供 `/observer` 手動啟動；三個 worker skill 由派工
   prompt 以路徑指名載入）。
2. 把 `agents/` 內三個範本複製到該 harness 的 agent 定義目錄（Claude Code：
   `~/.claude/agents/`），並把 `<TEAM_KIT_DIR>`／`<TEAM_KIT_ENG>` 換成**實際安裝位置**
   的絕對路徑（或自訂安裝位置的路徑）。未替換佔位符的 hook 掛不上、路徑讀不到。

## 安裝方式二：個人模式（單機目錄安裝）

現行個人安裝（`~/.claude/team-kit`）即此範本的實例：

1. 把整棵樹複製到 `~/.claude/team-kit`（`skills/` 內三個 worker skill 隨樹居住）。
2. 另把 `skills/observer/` 複製（或連結）到使用者 skill 目錄（`~/.claude/skills/observer`），
   讓 `/observer` 可以手動啟動。
3. 把 `agents/` 範本複製到 `~/.claude/agents/`，佔位符替換如下：
   `<TEAM_KIT_DIR>` → `~/.claude/team-kit` 所在的絕對路徑、
   `<TEAM_KIT_ENG>` → 該目錄下的 `eng`。

## 專案端與執行期狀態

- **專案 verify**：被驗專案的根目錄放 `team-kit.json`
  （`{"steps":[{"name":"build","cmd":"..."},{"name":"test","cmd":"..."}]}`）；
  coder 與 stop hook 都以 `TEAM_KIT_ROOT=<專案根>` 指向它。
- **執行期狀態**：所有狀態 artifact 寫在 `$AGENT_STATE_HOME`（未設定時 `~/.agent-state`）
  之下——路徑、格式與生命週期見 [`STATE-CONTRACT.md`](STATE-CONTRACT.md)。

## 測試

`sh eng/tests/run-tests.sh`——fixture 驅動，涵蓋兩個 hook 腳本的每個決定分支與
verify.sh 端到端（68 案）；測試以環境變數注入狀態根，不碰個人目錄。
