import os
import sys
import json
import datetime

# 修正 Windows 終端機 stdout/stderr cp950 編碼問題，強制使用 utf-8 輸出
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_JSON_PATH = os.path.join("archives", "topics.json")

def load_topics(json_path=DEFAULT_JSON_PATH):
    # 確保 archives 目錄存在
    os.makedirs(os.path.dirname(json_path) if os.path.dirname(json_path) else ".", exist_ok=True)
    
    if not os.path.exists(json_path):
        initial_data = {
            "topics": [
                {
                    "topic_id": "minimum_wage",
                    "topic_name": "最低工資法修法與青年就業",
                    "keywords_zh": ["最低工資法", "基本工資", "青年失業率", "CPI通膨"],
                    "keywords_en": ["Minimum Wage Law", "Youth Unemployment", "Basic Wage", "CPI Inflation"],
                    "status": "active",
                    "last_tracked_at": "2026-08-20 09:00:00"
                },
                {
                    "topic_id": "genai_hss",
                    "topic_name": "生成式 AI 對人文社會學科就業影響",
                    "keywords_zh": ["生成式AI", "人文社會學科", "文社科就業", "AI代工化"],
                    "keywords_en": ["Generative AI", "Humanities and Social Sciences", "HSS Employment", "AI Labor Displacement"],
                    "status": "active",
                    "last_tracked_at": "2026-08-22 14:30:00"
                }
            ]
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)
        return initial_data
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_topics(data, json_path=DEFAULT_JSON_PATH):
    os.makedirs(os.path.dirname(json_path) if os.path.dirname(json_path) else ".", exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_topics(json_path=DEFAULT_JSON_PATH):
    data = load_topics(json_path)
    print(f"=== 當前議題追蹤紀錄表 ({json_path}) ===")
    for idx, t in enumerate(data.get("topics", []), 1):
        status_icon = "[追蹤中]" if t["status"] == "active" else "[已暫停]"
        kw_zh = ", ".join(t.get("keywords_zh", []))
        kw_en = ", ".join(t.get("keywords_en", []))
        print(f"{idx}. {status_icon} {t['topic_name']} (ID: {t['topic_id']})")
        print(f"   - 中文關鍵字: {kw_zh}")
        print(f"   - 英文關鍵字: {kw_en}")
        print(f"   - 上次追蹤時間: {t.get('last_tracked_at', '從未追蹤')}")

def add_topic(topic_id, topic_name, kw_zh_str, kw_en_str="", json_path=DEFAULT_JSON_PATH):
    data = load_topics(json_path)
    keywords_zh = [k.strip() for k in kw_zh_str.split(",") if k.strip()]
    keywords_en = [k.strip() for k in kw_en_str.split(",") if k.strip()] if kw_en_str else []
    new_entry = {
        "topic_id": topic_id,
        "topic_name": topic_name,
        "keywords_zh": keywords_zh,
        "keywords_en": keywords_en,
        "status": "active",
        "last_tracked_at": "從未追蹤"
    }
    data["topics"].append(new_entry)
    save_topics(data, json_path)
    print(f"[成功] 新增中英雙語追蹤議題：{topic_name} (ID: {topic_id}) 至 {json_path}")

def toggle_status(topic_id, json_path=DEFAULT_JSON_PATH):
    data = load_topics(json_path)
    updated = False
    for t in data.get("topics", []):
        if t["topic_id"] == topic_id:
            t["status"] = "paused" if t["status"] == "active" else "active"
            print(f"[更新] 議題 [{t['topic_name']}] 狀態已更新為：{t['status']}")
            updated = True
            break
    if updated:
        save_topics(data, json_path)
    else:
        print(f"[錯誤] 找不到 ID 為 [{topic_id}] 的議題。")

def update_last_tracked(topic_id, json_path=DEFAULT_JSON_PATH):
    data = load_topics(json_path)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated = False
    for t in data.get("topics", []):
        if t["topic_id"] == topic_id or t["topic_name"] == topic_id:
            t["last_tracked_at"] = now_str
            updated = True
            print(f"[更新] 議題 [{t['topic_name']}] 上次追蹤時間已更新為：{now_str}")
            break
    if updated:
        save_topics(data, json_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_topics()
    else:
        cmd = sys.argv[1]
        if cmd == "list":
            list_topics()
        elif cmd == "add" and len(sys.argv) >= 4:
            kw_zh = sys.argv[4] if len(sys.argv) >= 5 else sys.argv[3]
            kw_en = sys.argv[5] if len(sys.argv) >= 6 else ""
            add_topic(sys.argv[2], sys.argv[3], kw_zh, kw_en)
        elif cmd == "toggle" and len(sys.argv) >= 3:
            toggle_status(sys.argv[2])
        elif cmd == "update" and len(sys.argv) >= 3:
            update_last_tracked(sys.argv[2])
        else:
            print("Usage:")
            print("  python manage_topics.py list")
            print("  python manage_topics.py add <topic_id> <topic_name> <keywords_zh_comma_separated> [keywords_en_comma_separated]")
            print("  python manage_topics.py toggle <topic_id>")
            print("  python manage_topics.py update <topic_id>")
