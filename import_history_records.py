"""
导入历史资料到知识库
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger, get_logger
import knowledge_base

setup_logger()
logger = get_logger(__name__)


def import_history_records():
    """导入历史资料"""
    history_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data',
        'human_civilization_history.json'
    )
    
    with open(history_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    logger.info(f"读取到 {len(records)} 条人类文明历史资料")
    
    kb = knowledge_base.get_knowledge_base()
    
    count = kb.add_history_records(records)
    
    logger.info(f"成功导入 {count} 条历史资料到知识库")
    
    stats = kb.get_history_stats()
    logger.info(f"知识库当前统计: {stats}")
    
    return count


if __name__ == "__main__":
    import_history_records()
