# Project Proposal: 多議題中英雙語縱向追蹤與 Subagent 併行處理 Agent (topic-tracker)

## 1. Project Overview (專案概述)
- **專案名稱：** Multi-Topic Bilingual Longitudinal Tracking Agent
- **團隊成員與分工：** 張同學（需求、topics.json 中英雙語與 Skill 設計）、李同學（Subagent 與 MCP 工具腳本整合）

## 2. Problem Domain & Background (問題領域與背景)
- **領域背景：** 人文社會學科研究者在進行專題與畢業論文時，需要同時長期觀察多個社會議題（如最低工資法修法、生成式 AI 就業衝擊、社會住宅政策）。
- **使用者痛點：** 手動每日搜尋多個議題極為耗時，單一中文檢索易遺漏國際視野，無法紀錄上次追蹤時間，且缺乏 Subagent 併行與時間序列資料庫工具。

## 3. Target Users & User Story (目標使用者與 User Story)
- **Target User Persona：** 人文社會學科大學生、研究生與政策研究員。
- **User Story：** 身為一位社會學研究生，我希望輸入 Topic Tracking 後，Agent 能讀取 `archives/topics.json` 中的中英文關鍵字請我選擇操作，對啟用議題發起 Subagent 雙軌檢索 `last_tracked_at` 後之國內外新聞並產出含中外 URL 引用之摘要，經我確認後自動歸檔至 `archives/` 並更新 `archives/topics.json` 時間戳記。

## 4. Agent Goal & Capability Boundary (Agent 目標與能力邊界)
- **Agent Goal：** 管理 `archives/topics.json` 雙語議題清單，經 HITL 1 確認後發起 Subagent 中英雙軌併行檢索，產出含中外 URL 引用之摘要，經 HITL 2 授權後寫入 `archives/YYYY-MM-DD_<topic>.md` 並更新 `archives/topics.json` 的 `last_tracked_at`。
- **能力邊界：** 
  - *In-Scope：* `archives/topics.json` 雙語關鍵字讀寫、HITL 1 議題選擇、Subagent 中英雙軌併行檢索、國內外資料來源 URL 引用、HITL 2 歸檔確認、磁碟寫入與時間戳記更新。
  - *Out-of-Scope：* 不進行即時電視新聞影音剪輯、不取代人類研究者的最終論文寫作。

## 5. Main Workflow & HITL Checkpoints (主要工作流與人機協同)
- **工作流步驟：** 讀取 `archives/topics.json` (中英關鍵字) $\rightarrow$ **【HITL 關卡一】議題管理與執行選擇** $\rightarrow$ 發起 Subagents 中英雙軌併行檢索 $\rightarrow$ 生成含中外 URL 引用之摘要草稿 $\rightarrow$ **【HITL 關卡二】摘要審查與歸檔授權** $\rightarrow$ 執行 `archive_digest.py` 寫檔並更新 `archives/topics.json` 時間。

## 6. System Architecture (系統架構圖)
```mermaid
graph TD
    User[使用者 (人文學者)] -->|Topic Tracking 需求| Prompt[Prompt / Conversation]
    Prompt --> Agent[Antigravity 2.0 Agent 核心]
    Agent <-->|讀寫狀態| TopicsJSON[Social_Topic/archives/topics.json]
    Agent <-->|讀寫檔案| Workspace[Social_Topic/archives/]
    Agent <-->|語意觸發 SOP| Skill[topic-tracker Skill Package]
    Agent <-->|發起雙軌併行處理| Subagents[Subagents 雙軌網絡]
    Subagents <-->|執行國內外新聞搜尋| Tools[Web Search & Filesystem Tools]
    Agent -->|交付當日摘要與索引| Result[Final Result]
```

## 7. Context Design (Context 工程設計)
- **Workspace 檔案規劃：** 建立 `Social_Topic/archives/topics.json` 記錄議題狀態與中英文關鍵字，建立 `Social_Topic/archives/` 保存每日 Markdown 摘要與全域 `INDEX.md`。
- **AGENTS.md 全域規範：** 規範輸出必須使用繁體中文，新聞與立場引用必須隨附國內外 URL Citation。

## 8. Agent Skills Design (Skill 套件設計)
- **Skill 名稱：** `topic-tracker`
- **YAML Description：** Tracks, searches, summarizes, and archives daily news on MULTIPLE social topics using archives/topics.json with BILINGUAL (Chinese & English) keyword matrices and Subagent execution with Human-in-the-Loop review.
- **內部配置：** `SKILL.md` (雙語 SOP+2大 HITL), `resources/summary_template.md` (含中外來源引用), `resources/trend_analysis_guide.md`, `examples/`, `scripts/manage_topics.py`, `scripts/archive_digest.py`.

## 9. MCP Servers & Tools (MCP 與工具整合)
- **採用的 Tools：** Web Search API / Filesystem Tools。
- **正當性說明：** Agent 需要即時擷取全網國內外新聞數據，Subagent 雙軌併行檢索，並將處理後的 Markdown 安全寫入磁碟並更新 `archives/topics.json`。

## 10. Expected Challenges & Risk Mitigation (預期挑戰與備案)
- **挑戰 1：** 英文關鍵字檢索結果過於龐雜。
  - *備案：* 在 `keywords_en` 中加上地域限定詞（如 "Taiwan minimum wage", "HSS employment AI"）精準縮小範疇。
- **挑戰 2：** 英文新聞未提供明確 URL 導致引用缺失。
  - *備案：* 在 `summary_template.md` 與 `SKILL.md` 中強制校驗引用格式，缺失時自動重搜補全。

## 11. Evaluation & Test Plan (驗證與測試計畫)
- **Happy Path 測試：** 輸入「議題追蹤」，順利讀取 `archives/topics.json` 觸發 HITL 1，啟動 Subagent 中英雙軌併行檢索，產出帶有國內外 URL 引用的摘要，於 HITL 2 授權後成功寫入 `archives/` 並更新 `archives/topics.json` 時間戳記。
- **Corner Case 測試：** 當使用者在 HITL 1 選擇新增議題但未填寫英文關鍵字時，Agent 應自動根據中文名稱翻譯補充預設英文關鍵字。

## 12. Project Schedule (4 週開發時程規劃)
- **Week 13：** 完成需求分析、系統架構設計與 `PROPOSAL.md`。
- **Week 14：** 建立 `Social_Topic/` Workspace、`archives/topics.json` 雙語結構、配置 `AGENTS.md` 並測試 Web Search 工具。
- **Week 15：** 完善 `topic-tracker` Skill 套件與 Subagent 雙軌併行邏輯，進行 Happy Path 與 Corner Case 測試。
- **Week 16：** 準備 Live Demo 簡報與專案成果展示。
