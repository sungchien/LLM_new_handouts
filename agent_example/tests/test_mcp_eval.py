import os
import sys
import unittest
import json

# 加入 src 路徑進行評估測試
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class TestTopicTrackerSystem(unittest.TestCase):
    """
    第 15 週 AI Agent 系統 Milestone 2 單元評估測試集 (Evaluation Suite)
    """

    def setUp(self):
        self.json_path = os.path.join("archives", "topics.json")

    def test_json_structure(self):
        """評估 1: 驗證持久化資料庫 archives/topics.json 是否存在且結構合法"""
        self.assertTrue(os.path.exists(self.json_path), "archives/topics.json 必須存在")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn("topics", data, "topics.json 必須包含 'topics' 根陣列")

    def test_bilingual_keywords(self):
        """評估 2: 驗證所有議題是否同時具備 keywords_zh 與 keywords_en 雙語陣列"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for t in data["topics"]:
            self.assertIn("keywords_zh", t, f"議題 {t['topic_id']} 缺失中文關鍵字")
            self.assertIn("keywords_en", t, f"議題 {t['topic_id']} 缺失英文關鍵字")
            self.assertGreater(len(t["keywords_zh"]), 0, "中文關鍵字不得為空")
            self.assertGreater(len(t["keywords_en"]), 0, "英文關鍵字不得為空")

    def test_index_markdown_exists(self):
        """評估 3: 驗證歸檔歷史全域索引檔 archives/INDEX.md 是否已建立"""
        index_path = os.path.join("archives", "INDEX.md")
        self.assertTrue(os.path.exists(index_path), "archives/INDEX.md 全域索引必須存在")

if __name__ == "__main__":
    unittest.main()
