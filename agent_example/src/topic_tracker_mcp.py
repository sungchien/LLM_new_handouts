import os
import sys
import json
import datetime
from mcp.server.fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("SocialTopicTrackerServer")

DEFAULT_JSON_PATH = os.path.join("archives", "topics.json")

# 動態匯入 manage_topics 模組 (SSOT 設計)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "skills", "topic-tracker", "scripts"))
if os.path.exists(SCRIPTS_DIR) and SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

try:
    import manage_topics
except ImportError:
    manage_topics = None

@mcp.tool()
def read_topic_registry(json_path: str = DEFAULT_JSON_PATH) -> str:
    """
    讀取 archives/topics.json 議題紀錄檔，傳回所有登錄議題的 ID、名稱、中英文關鍵字、追蹤狀態與上次追蹤時間。

    Args:
        json_path: 議題 JSON 紀錄檔的相對路徑，預設為 archives/topics.json。
    """
    if not os.path.exists(json_path):
        return f"ERROR: 找不到議題紀錄檔 [{json_path}]，請先確認專案 archives/ 目錄結構。"
    
    try:
        if manage_topics:
            data = manage_topics.load_topics(json_path)
        else:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"ERROR: 解析 topics.json 失敗: {str(e)}"

@mcp.tool()
def update_topic_tracking_time(topic_id: str, json_path: str = DEFAULT_JSON_PATH) -> str:
    """
    當議題完成新聞追蹤與歸檔後，更新指定 topic_id 在 archives/topics.json 中的 last_tracked_at 時間戳記為當前時間。

    Args:
        topic_id: 議題的不重複識別碼 (例如: minimum_wage, genai_hss)。
        json_path: 議題 JSON 紀錄檔路徑。
    """
    if not os.path.exists(json_path):
        return f"ERROR: 找不到議題紀錄檔 [{json_path}]。"
    
    try:
        if manage_topics:
            manage_topics.update_last_tracked(topic_id, json_path)
            return f"SUCCESS: 議題 [{topic_id}] 的 last_tracked_at 時間戳記已成功更新。"
        else:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = False
            for t in data.get("topics", []):
                if t.get("topic_id") == topic_id:
                    t["last_tracked_at"] = now_str
                    updated = True
                    break
            if updated:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return f"SUCCESS: 議題 [{topic_id}] 的 last_tracked_at 已更新為 {now_str}。"
            else:
                return f"ERROR: 找不到 ID 為 [{topic_id}] 的議題。"
    except Exception as e:
        return f"ERROR: 更新時間戳記失敗: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
