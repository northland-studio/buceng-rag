"""
删除指定来源的知识卡片
"""
from logger import get_logger
import knowledge_base

logger = get_logger(__name__)


def delete_cards_by_source(source_name: str):
    """
    删除指定来源的所有知识卡片
    
    Args:
        source_name: 来源名称
    
    Returns:
        删除的卡片数量
    """
    try:
        # 获取知识库实例
        kb = knowledge_base.get_knowledge_base()
        
        # 获取所有卡片（需要遍历）
        # 由于ChromaDB没有直接按元数据删除的方法，我们需要先查询再删除
        
        # 使用一个通用的查询来获取所有卡片
        # 这里我们使用一个空查询或者特殊查询
        all_cards = kb.collection.get(
            include=['metadatas', 'documents']
        )
        
        if not all_cards or not all_cards['ids']:
            logger.info("知识库中没有卡片")
            return 0
        
        # 找到所有匹配来源的卡片ID
        ids_to_delete = []
        for i, card_id in enumerate(all_cards['ids']):
            metadata = all_cards['metadatas'][i]
            if metadata.get('source') == source_name:
                ids_to_delete.append(card_id)
        
        if not ids_to_delete:
            logger.info(f"没有找到来源为 '{source_name}' 的卡片")
            return 0
        
        logger.info(f"找到 {len(ids_to_delete)} 张来源为 '{source_name}' 的卡片")
        
        # 删除卡片
        kb.collection.delete(ids=ids_to_delete)
        
        logger.info(f"成功删除 {len(ids_to_delete)} 张卡片")
        
        return len(ids_to_delete)
        
    except Exception as e:
        logger.error(f"删除卡片失败: {e}")
        return 0


if __name__ == "__main__":
    source_name = "玄剑公会通史文印版.pdf"
    count = delete_cards_by_source(source_name)
    print(f"删除完成：成功删除 {count} 张卡片")
