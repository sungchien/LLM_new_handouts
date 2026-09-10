import os
import sys
import datetime
import re
import json

# 修正 Windows 終端機 stdout/stderr cp950 編碼問題，強制使用 utf-8 輸出
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 引用同目錄下的 manage_topics 模組 (Single Source of Truth)
try:
    import manage_topics
except ImportError:
    manage_topics = None

DEFAULT_JSON_PATH = os.path.join("archives", "topics.json")

def archive_summary(topic_id, topic_name, markdown_content, base_dir="archives", json_path=DEFAULT_JSON_PATH):
    """
    將產出的摘要自動歸檔至 archives/YYYY-MM-DD_<topic>.md，
    維護 archives/INDEX.md 全域目錄，並呼叫 manage_topics 同步更新 archives/topics.json 中的 last_tracked_at 時間。
    """
    os.makedirs(base_dir, exist_ok=True)
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    now_full_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_topic = re.sub(r'[^\w\-_\u4e00-\u9fa5]', '_', topic_name).strip('_')
    filename = f"{today_str}_{safe_topic}.md"
    file_path = os.path.join(base_dir, filename)
    
    # 1. 寫入當日摘要檔 (強制要求包含來源引用)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"[成功] 成功歸檔摘要檔至：{file_path}")
    
    # 2. 更新 INDEX.md 全域索引
    index_path = os.path.join(base_dir, "INDEX.md")
    index_entry = f"- [{today_str}] [{topic_name}]({filename})\n"
    
    existing_content = ""
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    else:
        existing_content = "# 議題歸檔歷史全域索引 (Archive Index)\n\n"
        
    if index_entry not in existing_content:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(existing_content + index_entry)
        print(f"[索引] 全域索引已更新：{index_path}")
        
    # 3. 同步更新 archives/topics.json 中的 last_tracked_at 時間
    if manage_topics:
        manage_topics.update_last_tracked(topic_id, json_path)
    else:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                updated = False
                for t in data.get("topics", []):
                    if t.get("topic_id") == topic_id or t.get("topic_name") == topic_name:
                        t["last_tracked_at"] = now_full_str
                        updated = True
                        break
                if updated:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"[更新] {json_path} 中 [{topic_name}] 的追蹤時間已更新為：{now_full_str}")
            except Exception as e:
                print(f"[警告] 更新 {json_path} 失敗: {e}")

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        topic_id = sys.argv[1]
        topic_name = sys.argv[2]
        content_file = sys.argv[3]
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        archive_summary(topic_id, topic_name, content)
    else:
        print("Usage: python archive_digest.py <topic_id> <topic_name> <path_to_summary_markdown>")
