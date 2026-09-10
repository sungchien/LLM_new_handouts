---
name: topic-tracker
description: >
  Tracks, searches, summarizes, and archives daily news on MULTIPLE social topics using archives/topics.json
  with BILINGUAL (Chinese & English) keyword matrices, Subagent execution, Edge Case handling, and Human-in-the-Loop review.
  Use this skill when the user requests Topic Tracking, 議題追蹤, bilingual news tracking, or topic registry management.
---

# Instructions: 多議題中英雙語縱向追蹤與 Subagent 併行處理 SOP (Human-in-the-Loop & Edge Cases)

當使用者觸發「Topic Tracking」、「議題追蹤」或查詢議題清單時，請遵循以下**多議題管理、中英雙語檢索、Subagent 執行、Edge Case 例外防禦與雙重 HITL 審查**標準流程：

---

## 第一階段：讀取議題紀錄檔 (Topic Registry Inspection)
1. 呼叫 MCP 工具 `read_topic_registry()` 或執行腳本 `scripts/manage_topics.py list`，讀取 **`archives/topics.json`** 議題紀錄檔。
2. 列出目前所有登錄的議題，包含：
   - 議題 ID (`topic_id`) 與 議題名稱 (`topic_name`)
   - **中英雙語檢索關鍵字列表** (`keywords_zh` 與 `keywords_en`)
   - 追蹤狀態 (`status`: 🟢 追蹤中 / ⏸️ 已暫停)
   - 上次追蹤時間 (`last_tracked_at`)

---

## 🛑 關卡一：Human-in-the-Loop 雙語議題管理與執行確認 (HITL Checkpoint 1)
**向使用者展示中英雙語議題清單面板，並詢問操作意向：**

> 「**【多議題中英雙語追蹤管理面板】**  
> 目前登錄於 `archives/topics.json` 的議題清單如下：  
> `[列出所有議題狀態、中英文關鍵字與上次追蹤時間]`  
> 
> 請選擇您要執行的操作：  
> 1. 🚀 **開始追蹤**：發起所有「🟢 追蹤中」議題的中英文最新資訊檢索。  
> 2. ⏸️ **狀態切換**：暫停或恢復特定議題（請提供 topic_id）。  
> 3. ➕ **新增議題**：登錄全新追蹤議題（請提供議題名稱、中文關鍵字與英文關鍵字）。」

---

## 第二階段：Subagent 中英雙軌併行追蹤與 Edge Case 處理 (Bilingual Subagents & Edge Cases)
對每一個處於「🟢 追蹤中」狀態的議題，**啟動 Subagent** 進行併行檢索：

1. **時間過濾與雙軌檢索**：
   - **中文軌道 (`keywords_zh`)**：檢索國內媒體、政府公報與在地報導。
   - **英文軌道 (`keywords_en`)**：檢索國際權威媒體（如 Reuters, Bloomberg）、學術期刊與智庫。

2. **⚠️ Edge Case 邊界例外防禦**：
   - **例外 1 (檢索 0 結果)**：若特定議題在 `last_tracked_at` 後無任何最新新聞，Subagent 不得憑空捏造，應明確標記「自 {{LAST_TRACKED_AT}} 以來無最新動態」，並於草稿中提示使用者是否放寬檢索時間或關鍵字。
   - **例外 2 (JSON 損毀/缺失)**：若 `archives/topics.json` 不存在，自動觸發 `manage_topics.py` 建構預設雙語議題紀錄檔。

---

## 第三階段：結構化摘要與中外來源標註 (Bilingual Digest Synthesis with Citations)
Subagent 參照 `resources/summary_template.md` 生成當日摘要，**必須嚴格遵守以下兩點**：
1. **中外資料來源標註（Mandatory Global Citations）**：每一條動態與立場均須標註明確的來源出處（含國內媒體與國際英文媒體之標題、發表時間與原始 URL 連結）。
2. **國內外視角對比**：摘要中須單獨對比國內討論焦點與國際報導趨勢的異同。

---

## 🛑 關卡二：Human-in-the-Loop 摘要審查與歸檔授權 (HITL Checkpoint 2)
**Subagent 產出中英雙語摘要草稿後，展示草稿並詢問歸檔意願：**

> 「**【中英雙語議題追蹤摘要審查：{{TOPIC_NAME}}】**  
> 已完成自 `{{LAST_TRACKED_AT}}` 以來的最新國內外動態摘要草稿（如下，包含國內外新聞來源引用）。  
> 
> 請問是否同意儲存此摘要？同意後將寫入 `archives/YYYY-MM-DD_<topic>.md` 並同步更新 `archives/topics.json` 的上次追蹤時間。」

- **⚠️ Edge Case 例外處理 (使用者不同意儲存)**：若使用者選擇「不同意」或要求修訂，Agent 不得執行歸檔腳本，必須提供草稿修改選項，或安全退出對話。

---

## 第四階段：寫入 `archives/` 與更新 `archives/topics.json` (Archiving & JSON Update)
1. 使用者同意儲存後，執行：
   `python skills/topic-tracker/scripts/archive_digest.py <topic_id> <topic_name> <summary_draft_path>`
2. 腳本自動完成：
   - 寫入 `archives/YYYY-MM-DD_<topic>.md`（含中外來源引用）。
   - 更新 `archives/INDEX.md` 全域索引。
   - **同步更新 `archives/topics.json`** 中該議題的 `last_tracked_at` 為當前時間。
