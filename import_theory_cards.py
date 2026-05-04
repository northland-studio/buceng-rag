"""
导入社会科学理论卡片到知识库
"""
import json
from pathlib import Path

from logger import get_logger
from config import settings
import knowledge_base

logger = get_logger(__name__)


def import_theory_cards():
    """导入理论卡片到知识库"""
    try:
        # 读取理论卡片文件
        cards_file = Path(settings.DATA_DIR) / "social_theory_cards.json"
        
        if not cards_file.exists():
            logger.error(f"理论卡片文件不存在: {cards_file}")
            return 0
        
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        
        logger.info(f"读取到 {len(cards)} 张理论卡片")
        
        # 获取知识库实例
        kb = knowledge_base.get_knowledge_base()
        
        # 导入卡片
        count = kb.add_cards(cards)
        
        logger.info(f"成功导入 {count} 张理论卡片到知识库")
        
        return count
        
    except Exception as e:
        logger.error(f"导入理论卡片失败: {e}")
        return 0


if __name__ == "__main__":
    count = import_theory_cards()
    print(f"导入完成：成功导入 {count} 张理论卡片")
