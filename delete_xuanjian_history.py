"""
删除玄剑公会通史历史卡片
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger, get_logger
import knowledge_base

setup_logger()
logger = get_logger(__name__)


def delete_xuanjian_history():
    """删除玄剑公会通史历史卡片"""
    kb = knowledge_base.get_knowledge_base()
    
    history_collection = kb.history_collection
    
    all_records = history_collection.get()
    
    if not all_records or not all_records['ids']:
        logger.info("历史资料库为空")
        return 0
    
    ids_to_delete = []
    for record_id in all_records['ids']:
        if record_id.startswith('xuanjian_history_'):
            ids_to_delete.append(record_id)
    
    if not ids_to_delete:
        logger.info("没有找到玄剑公会通史历史卡片")
        return 0
    
    logger.info(f"找到 {len(ids_to_delete)} 条玄剑公会通史历史卡片")
    
    history_collection.delete(ids=ids_to_delete)
    
    logger.info(f"成功删除 {len(ids_to_delete)} 条玄剑公会通史历史卡片")
    
    stats = kb.get_history_stats()
    logger.info(f"知识库当前统计: {stats}")
    
    return len(ids_to_delete)


if __name__ == "__main__":
    delete_xuanjian_history()
