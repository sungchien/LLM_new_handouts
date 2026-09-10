---
name: topic-tracker
description: >
  Tracks, searches, summarizes, and archives daily news on MULTIPLE social topics using archives/topics.json
  with BILINGUAL (Chinese & English) keyword matrices and Subagent execution with Human-in-the-Loop review.
  Use this skill when the user requests Topic Tracking, 議題追蹤, bilingual news tracking, or topic registry management.
---

# Instructions: 多議題中英雙語縱向追蹤與 Subagent 併行處理 SOP (Human-in-the-Loop)

當使用者觸發「Topic Tracking」、「議題追蹤」或查詢議題清單時，請遵循以下**多議題管理、中英雙語檢索、Subagent 執行與雙重 HITL 審查**標準流程：

---

## 第一階段：讀取議題紀錄檔 (Topic Registry Inspection)
1. 執行 Python 腳本 `scripts/manage_topics.py list`，讀取保存在 **`archives/topics.json`** 的議題紀錄檔。
2. 列出目前所有登錄的議題，包含：
   - 議題 ID (`topic_id`) 與 議題名稱 (`topic_name`)
   - **中英雙語檢索關鍵字列表** (`keywords_zh` 與 `keywords_en`)
   - 追蹤狀態 (`status`: 🟢 追蹤中 / ⏸️ 已暫停)
   - 上次追蹤時間 (`last_tracked_at`)

---

## 🛑 關卡一：Human-in-the-Loop 雙語議題管理與執行確認 (HITL Checkpoint 1)
**在發起網路檢索前，向使用者展示中英雙語議題清單面板，並詢問操作意向：**

> 「**【多議題中英雙語追蹤管理面板】**  
> 目前登錄於 `archives/topics.json` 的議題清單如下：  
> `[列出所有議題狀態、中英文關鍵字與上次追蹤時間]`  
> 
> 請選擇您要執行的操作：  
> 1. 🚀 **開始追蹤**：發起所有「🟢 追蹤中」議題的中英文最新資訊檢索。  
> 2. ⏸️ **狀態切換**：暫停或恢復特定議題（請提供 topic_id）。  
> 3. ➕ **新增議題**：登錄全新追蹤議題（請提供議題名稱、中文關鍵字與英文關鍵字）。」

*等待使用者回應或修改 `archives/topics.json` 後，才進入第二階段。*

---

## 第二階段：Subagent 中英雙語併行追蹤 (Subagent Bilingual Parallel Tracking)
對每一個處於「🟢 追蹤中」狀態的議題，**啟動 Subagent（或獨立對話串）** 進行併行檢索：

1. **時間維度過濾**：根據該議題的 `last_tracked_at` 時間，檢索該時間點之後發布的國內外最新新聞與評論。
2. **中英雙語雙軌檢索（Bilingual Dual Search Strategy）**：
   - **中文軌道 (`keywords_zh`)**：檢索國內媒體、政府公報與華文論壇（了解在地政策脈絡與團體主張）。
   - **英文軌道 (`keywords_en`)**：檢索國際權威媒體（如 Reuters, Bloomberg, NYT）、學術期刊與國際智庫（擴大全球視角與國際趨勢比對）。

---

## 第三階段：結構化摘要與中外來源標註 (Bilingual Digest Synthesis with Citations)
Subagent 參照 `resources/summary_template.md` 生成當日摘要，**必須嚴格遵守以下兩點**：
1. **中外資料來源標註（Mandatory Global Citations）**：每一條動態與立場均須標註明確的來源出處（含國內媒體與國際英文媒體之標題、發表時間與原始 URL 連結）。
2. **國內外視角對比**：摘要中須單獨對比國內討論焦點與國際報導趨勢的異同。

---

## 🛑 關卡二：Human-in-the-Loop 摘要審查與歸檔授權 (HITL Checkpoint 2)
**Subagent 產出中英雙語摘要草稿後，停下來向使用者展示草稿並詢問歸檔意願：**

> 「**【中英雙語議題追蹤摘要審查：{{TOPIC_NAME}}】**  
> 已完成自 `{{LAST_TRACKED_AT}}` 以來的最新國內外動態摘要草稿（如下，包含國內外新聞來源引用）。  
> 
> 請問是否同意儲存此摘要？同意後將寫入 `archives/YYYY-MM-DD_<topic>.md` 並同步更新 `archives/topics.json` 的上次追蹤時間。」

---

## 第四階段：寫入 `archives/` 與更新 `archives/topics.json` (Archiving & JSON Update)
1. 使用者同意儲存後，執行：
   `python scripts/archive_digest.py <topic_id> <topic_name> <summary_draft_path>`
2. 腳本會自動完成三項任務：
   - 寫入歸檔檔案 `archives/YYYY-MM-DD_<topic>.md`（包含中外完整來源引用）。
   - 更新全域索引檔案 `archives/INDEX.md`。
   - **同步更新 `archives/topics.json`** 中該議題的 `last_tracked_at` 為當前時間戳記。
