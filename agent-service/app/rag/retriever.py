"""
RAG检索器
简单的关键词匹配检索（TODO: 替换为向量检索）
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class KnowledgeRetriever:
    """知识库检索器"""

    def __init__(self, knowledge_base_path: str = None):
        if knowledge_base_path is None:
            knowledge_base_path = str(Path(__file__).parent / "knowledge_base")

        self.knowledge_base_path = Path(knowledge_base_path)
        self._load_knowledge()

    def _load_knowledge(self):
        """加载知识库"""
        self.knowledge = {}

        # 加载鼓励话术
        encouragement_path = self.knowledge_base_path / "encouragement" / "encouragement.json"
        if encouragement_path.exists():
            with open(encouragement_path, "r", encoding="utf-8") as f:
                self.knowledge["encouragement"] = json.load(f)

        # 加载考试策略
        strategies_path = self.knowledge_base_path / "exam_strategies" / "strategies.json"
        if strategies_path.exists():
            with open(strategies_path, "r", encoding="utf-8") as f:
                self.knowledge["exam_strategies"] = json.load(f)

        # 加载彩蛋
        easter_eggs_path = self.knowledge_base_path / "easter_eggs" / "easter_eggs.json"
        if easter_eggs_path.exists():
            with open(easter_eggs_path, "r", encoding="utf-8") as f:
                self.knowledge["easter_eggs"] = json.load(f)

        # 加载闲聊
        small_talk_path = self.knowledge_base_path / "small_talk" / "small_talk.json"
        if small_talk_path.exists():
            with open(small_talk_path, "r", encoding="utf-8") as f:
                self.knowledge["small_talk"] = json.load(f)

        # 加载校园信息
        campus_path = self.knowledge_base_path / "campus_info" / "campus.json"
        if campus_path.exists():
            with open(campus_path, "r", encoding="utf-8") as f:
                self.knowledge["campus"] = json.load(f)

    def get_encouragement(self, completion_rate: float) -> Dict[str, Any]:
        """根据完成率获取鼓励话术"""
        if completion_rate >= 100:
            level = "level_100"
        elif completion_rate >= 75:
            level = "level_75"
        elif completion_rate >= 50:
            level = "level_50"
        elif completion_rate >= 25:
            level = "level_25"
        else:
            level = "level_10"

        return self.knowledge.get("encouragement", {}).get("encouragement_levels", {}).get(level, {})

    def get_streak_reward(self, streak_days: int) -> Optional[Dict[str, Any]]:
        """根据连续天数获取奖励"""
        streak_map = {
            3: "3_days",
            5: "5_days",
            7: "7_days",
            14: "14_days",
            30: "30_days"
        }

        key = streak_map.get(streak_days)
        if key:
            return self.knowledge.get("encouragement", {}).get("streak_rewards", {}).get(key)
        return None

    def get_exam_strategy(self, exam_type: str, phase: int) -> Dict[str, Any]:
        """获取考试策略"""
        phases = {1: "基础阶段", 2: "强化阶段", 3: "冲刺阶段"}
        phase_name = phases.get(phase, "基础阶段")

        return self.knowledge.get("exam_strategies", {}).get("exam_types", {}).get(exam_type, {}).get("phases", {}).get(phase_name, {})

    def get_comfort_word(self, emotion: str) -> str:
        """获取安慰话术"""
        import random

        words = self.knowledge.get("encouragement", {}).get("comfort_words", {}).get(emotion, [])
        return random.choice(words) if words else "小搭陪着你～"

    def get_easter_egg(self, egg_type: str) -> Optional[str]:
        """获取彩蛋内容"""
        import random

        eggs = self.knowledge.get("easter_eggs", {}).get("easter_eggs", {}).get(egg_type, {}).get("messages", [])
        return random.choice(eggs) if eggs else None

    def get_small_talk(self, category: str, key: str) -> str:
        """获取闲聊回复"""
        import random

        responses = self.knowledge.get("small_talk", {}).get("small_talk", {}).get(category, {}).get(key, [])
        return random.choice(responses) if responses else "小搭在听～"

    def get_random_tip(self) -> str:
        """获取随机小贴士"""
        import random

        tips = self.knowledge.get("small_talk", {}).get("small_talk", {}).get("daily_tips", [])
        return random.choice(tips) if tips else "加油！"


# 全局检索器实例
_retriever: Optional[KnowledgeRetriever] = None


def get_retriever() -> KnowledgeRetriever:
    """获取检索器单例"""
    global _retriever
    if _retriever is None:
        _retriever = KnowledgeRetriever()
    return _retriever