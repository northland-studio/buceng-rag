"""
查看知识库中所有卡片的来源
"""
from logger import get_logger
import knowledge_base
from collections import Counter

logger = get_logger(__name__)


def list_all_sources():
    """
    列出知识库中所有卡片的来源
    
    Returns:
        来源统计字典
    """
    try:
        # 获取知识库实例
        kb = knowledge_base.get_knowledge_base()
        
        # 获取所有卡片
        all_cards = kb.collection.get(
            include=['metadatas']
        )
        
        if not all_cards or not all_cards['ids']:
            logger.info("知识库中没有卡片")
            return {}
        
        # 统计来源
        sources = []
        for metadata in all_cards['metadatas']:
            source = metadata.get('source', '未知来源')
            sources.append(source)
        
        # 计数
        source_counts = Counter(sources)
        
        # 打印结果
        print("\n知识库卡片来源统计：")
        print("=" * 50)
        for source, count in source_counts.most_common():
            print(f"{source}: {count}张")
        print("=" * 50)
        print(f"总计: {len(sources)}张卡片")
        
        return dict(source_counts)
        
    except Exception as e:
        logger.error(f"获取来源列表失败: {e}")
        return {}


if __name__ == "__main__":
    sources = list_all_sources()
