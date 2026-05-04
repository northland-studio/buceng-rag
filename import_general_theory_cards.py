"""
导入现实社科理论原文知识卡片到知识库
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger, get_logger
import knowledge_base

setup_logger()
logger = get_logger(__name__)


def import_general_theory_cards():
    """导入现实社科理论卡片"""
    cards_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data',
        'general_social_theory_cards.json'
    )
    
    with open(cards_file, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    logger.info(f"读取到 {len(cards)} 张现实社科理论卡片")
    
    kb = knowledge_base.get_knowledge_base()
    
    count = kb.add_cards(cards)
    
    logger.info(f"成功导入 {count} 张卡片到知识库")
    
    stats = kb.get_stats()
    logger.info(f"知识库当前统计: {stats}")
    
    return count


if __name__ == "__main__":
    import_general_theory_cards()
