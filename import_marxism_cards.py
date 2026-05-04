"""
导入马列毛经典著作原文知识卡片到知识库
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger, get_logger
import knowledge_base

setup_logger()
logger = get_logger(__name__)


def import_marxism_cards():
    """导入马列毛经典著作卡片"""
    cards_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data',
        'marxism_leninism_mao_cards.json'
    )
    
    with open(cards_file, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    logger.info(f"读取到 {len(cards)} 张马列毛经典著作卡片")
    
    kb = knowledge_base.get_knowledge_base()
    
    count = kb.add_cards(cards)
    
    logger.info(f"成功导入 {count} 张卡片到知识库")
    
    stats = kb.get_stats()
    logger.info(f"知识库当前统计: {stats}")
    
    return count


if __name__ == "__main__":
    import_marxism_cards()
