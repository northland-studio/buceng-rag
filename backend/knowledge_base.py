"""
知识库模块
管理ChromaDB向量数据库，提供理论卡片的存储和检索功能
"""
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api import EmbeddingFunction

from logger import get_logger
from config import settings
from exceptions import (
    KnowledgeBaseError,
    CollectionNotFoundError,
    CardNotFoundError,
    DuplicateCardError,
    FileParseError
)
import embedding

logger = get_logger(__name__)


class LocalEmbeddingFunction(EmbeddingFunction):
    """
    ChromaDB自定义嵌入函数
    使用本地嵌入模型生成向量
    """
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        为文本列表生成嵌入向量
        
        Args:
            input: 文本列表
        
        Returns:
            嵌入向量列表
        """
        return embedding.get_embeddings(input, normalize=True)


class KnowledgeBase:
    """
    知识库管理类
    
    管理理论卡片的存储、检索和更新
    同时管理历史资料库
    """
    
    def __init__(self):
        """初始化知识库"""
        self._client: Optional[chromadb.Client] = None
        self._collection: Optional[chromadb.Collection] = None
        self._golden_collection: Optional[chromadb.Collection] = None
        self._history_collection: Optional[chromadb.Collection] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """
        初始化ChromaDB客户端和集合
        
        Raises:
            KnowledgeBaseError: 初始化失败
        """
        if self._initialized:
            return
        
        try:
            # 确保持久化目录存在
            chroma_path = settings.get_chroma_path()
            chroma_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"初始化ChromaDB，持久化目录: {chroma_path}")
            
            # 创建ChromaDB客户端
            self._client = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 创建嵌入函数
            embedding_fn = LocalEmbeddingFunction()
            
            # 获取或创建主集合
            self._collection = self._client.get_or_create_collection(
                name=settings.COLLECTION_NAME,
                embedding_function=embedding_fn,
                metadata={"description": "Minecraft社会学理论卡片"}
            )
            
            # 获取或创建黄金样本集合
            self._golden_collection = self._client.get_or_create_collection(
                name=settings.GOLDEN_SAMPLES_COLLECTION,
                embedding_function=embedding_fn,
                metadata={"description": "黄金样本数据"}
            )
            
            # 获取或创建历史资料集合
            self._history_collection = self._client.get_or_create_collection(
                name=settings.HISTORY_COLLECTION,
                embedding_function=embedding_fn,
                metadata={"description": "历史资料记录"}
            )
            
            logger.info(
                f"知识库初始化成功，"
                f"理论卡片数: {self._collection.count()}，"
                f"黄金样本数: {self._golden_collection.count()}，"
                f"历史资料数: {self._history_collection.count()}"
            )
            
            self._initialized = True
            
            # 如果集合为空，尝试加载初始数据
            if self._collection.count() == 0:
                self._load_seed_cards()
            
        except Exception as e:
            logger.error(f"知识库初始化失败: {e}")
            raise KnowledgeBaseError(
                message="知识库初始化失败",
                details=str(e)
            )
    
    def _load_seed_cards(self) -> None:
        """
        加载初始理论卡片
        
        Raises:
            FileParseError: 文件解析失败
        """
        seed_file = settings.get_data_path(settings.SEED_CARDS_FILE)
        
        if not seed_file.exists():
            logger.warning(f"初始卡片文件不存在: {seed_file}")
            return
        
        try:
            with open(seed_file, 'r', encoding='utf-8') as f:
                cards = json.load(f)
            
            if cards:
                self.add_cards(cards)
                logger.info(f"成功加载 {len(cards)} 张初始理论卡片")
            
        except Exception as e:
            logger.error(f"加载初始卡片失败: {e}")
            raise FileParseError(
                file_path=str(seed_file),
                details=str(e)
            )
    
    @property
    def client(self) -> chromadb.Client:
        """获取ChromaDB客户端"""
        if not self._initialized:
            self.initialize()
        return self._client
    
    @property
    def collection(self) -> chromadb.Collection:
        """获取理论卡片集合"""
        if not self._initialized:
            self.initialize()
        return self._collection
    
    @property
    def golden_collection(self) -> chromadb.Collection:
        """获取黄金样本集合"""
        if not self._initialized:
            self.initialize()
        return self._golden_collection
    
    @property
    def history_collection(self) -> chromadb.Collection:
        """获取历史资料集合"""
        if not self._initialized:
            self.initialize()
        return self._history_collection
    
    def add_cards(self, cards: List[Dict[str, Any]]) -> int:
        """
        添加理论卡片到知识库
        
        Args:
            cards: 卡片列表，每个卡片包含:
                - id: 唯一标识
                - title: 标题
                - content: 内容
                - keywords: 关键词列表
                - source: 来源
        
        Returns:
            成功添加的卡片数量
        
        Raises:
            DuplicateCardError: 卡片ID重复
        """
        if not cards:
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for card in cards:
            card_id = card.get('id')
            if not card_id:
                logger.warning(f"卡片缺少ID，跳过: {card}")
                continue
            
            # 检查是否已存在
            existing = self.collection.get(ids=[card_id])
            if existing and existing['ids']:
                logger.warning(f"卡片ID已存在，跳过: {card_id}")
                continue
            
            ids.append(card_id)
            documents.append(card.get('content', ''))
            
            metadata = {
                'title': card.get('title', ''),
                'keywords': ','.join(card.get('keywords', [])),
                'source': card.get('source', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            metadatas.append(metadata)
        
        if ids:
            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(f"成功添加 {len(ids)} 张理论卡片")
                return len(ids)
            except Exception as e:
                logger.error(f"添加卡片失败: {e}")
                raise KnowledgeBaseError(
                    message="添加理论卡片失败",
                    details=str(e)
                )
        
        return 0
    
    def search_similar(
        self,
        query: str,
        k: int = None,
        where: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        检索相似的理论卡片
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认使用配置值
            where: 元数据过滤条件
        
        Returns:
            相似卡片列表，每个包含:
                - id: 卡片ID
                - title: 标题
                - content: 内容
                - source: 来源
                - keywords: 关键词列表
                - similarity: 相似度分数 (0-1)
        """
        if k is None:
            k = settings.MAX_RETRIEVAL_RESULTS
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )
            
            cards = []
            if results and results['ids'] and results['ids'][0]:
                for i, card_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    # 将距离转换为相似度 (1 - distance)
                    similarity = max(0, 1 - distance)
                    
                    metadata = results['metadatas'][0][i]
                    
                    card = {
                        'id': card_id,
                        'title': metadata.get('title', ''),
                        'content': results['documents'][0][i],
                        'source': metadata.get('source', ''),
                        'keywords': metadata.get('keywords', '').split(',') if metadata.get('keywords') else [],
                        'similarity': round(similarity, 4)
                    }
                    cards.append(card)
            
            logger.info(f"检索到 {len(cards)} 张相关卡片")
            return cards
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            raise KnowledgeBaseError(
                message="检索理论卡片失败",
                details=str(e)
            )
    
    def search(self, query: str, k: int = None, where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        检索相似的理论卡片 (search_similar 的别名)
        
        Args:
            query: 查询文本
            k: 返回结果数量
            where: 元数据过滤条件
        
        Returns:
            相似卡片列表
        """
        return self.search_similar(query, k, where)
    
    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定ID的理论卡片
        
        Args:
            card_id: 卡片ID
        
        Returns:
            卡片信息，不存在则返回None
        """
        try:
            result = self.collection.get(
                ids=[card_id],
                include=['documents', 'metadatas']
            )
            
            if result and result['ids']:
                metadata = result['metadatas'][0]
                return {
                    'id': card_id,
                    'title': metadata.get('title', ''),
                    'content': result['documents'][0],
                    'source': metadata.get('source', ''),
                    'keywords': metadata.get('keywords', '').split(',') if metadata.get('keywords') else []
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取卡片失败: {e}")
            return None
    
    def get_all_cards(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        获取所有理论卡片
        
        Args:
            limit: 最大返回数量
        
        Returns:
            卡片列表
        """
        try:
            result = self.collection.get(
                limit=limit,
                include=['documents', 'metadatas']
            )
            
            cards = []
            if result and result['ids']:
                for i, card_id in enumerate(result['ids']):
                    metadata = result['metadatas'][i] if result['metadatas'] else {}
                    cards.append({
                        'id': card_id,
                        'title': metadata.get('title', ''),
                        'content': result['documents'][i] if result['documents'] else '',
                        'category': metadata.get('category', 'general'),
                        'source': metadata.get('source', ''),
                        'keywords': metadata.get('keywords', '').split(',') if metadata.get('keywords') else []
                    })
            
            return cards
            
        except Exception as e:
            logger.error(f"获取所有卡片失败: {e}")
            return []
    
    def update_card(self, card_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新理论卡片
        
        Args:
            card_id: 卡片ID
            updates: 更新内容
        
        Returns:
            是否更新成功
        """
        try:
            # 先获取现有卡片
            existing = self.get_card(card_id)
            if not existing:
                raise CardNotFoundError(card_id)
            
            # 准备更新数据
            document = updates.get('content', existing['content'])
            metadata = {
                'title': updates.get('title', existing['title']),
                'keywords': ','.join(updates.get('keywords', existing['keywords'])),
                'source': updates.get('source', existing['source']),
                'created_at': existing.get('created_at', ''),
                'updated_at': datetime.now().isoformat()
            }
            
            self.collection.update(
                ids=[card_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            logger.info(f"卡片更新成功: {card_id}")
            return True
            
        except CardNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新卡片失败: {e}")
            return False
    
    def delete_card(self, card_id: str) -> bool:
        """
        删除理论卡片
        
        Args:
            card_id: 卡片ID
        
        Returns:
            是否删除成功
        """
        try:
            self.collection.delete(ids=[card_id])
            logger.info(f"卡片删除成功: {card_id}")
            return True
        except Exception as e:
            logger.error(f"删除卡片失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            return {
                'total_cards': self.collection.count(),
                'golden_samples': self.golden_collection.count(),
                'history_records': self.history_collection.count(),
                'collection_name': settings.COLLECTION_NAME,
                'persist_directory': str(settings.get_chroma_path())
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def add_golden_sample(
        self,
        event: str,
        analysis: str,
        rating: int,
        retrieved_cards: Optional[List[str]] = None
    ) -> bool:
        """
        添加黄金样本
        
        Args:
            event: 事件文本
            analysis: 分析结果
            rating: 评分 (1-3)
            retrieved_cards: 检索到的卡片ID列表
        
        Returns:
            是否添加成功
        """
        try:
            # 生成唯一ID
            sample_id = f"golden_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            # 准备元数据
            metadata = {
                'rating': rating,
                'retrieved_cards': ','.join(retrieved_cards) if retrieved_cards else '',
                'created_at': datetime.now().isoformat()
            }
            
            # 文档内容
            document = f"事件: {event}\n\n分析: {analysis}"
            
            self.golden_collection.add(
                ids=[sample_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            logger.info(f"黄金样本添加成功: {sample_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加黄金样本失败: {e}")
            return False
    
    def export_golden_samples(self, output_file: str) -> int:
        """
        导出黄金样本到JSONL文件
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            导出的样本数量
        """
        try:
            # 获取所有黄金样本
            results = self.golden_collection.get(
                include=['documents', 'metadatas']
            )
            
            if not results or not results['ids']:
                logger.info("没有黄金样本可导出")
                return 0
            
            # 写入JSONL文件
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, sample_id in enumerate(results['ids']):
                    sample = {
                        'id': sample_id,
                        'document': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
            
            logger.info(f"成功导出 {len(results['ids'])} 个黄金样本到 {output_file}")
            return len(results['ids'])
            
        except Exception as e:
            logger.error(f"导出黄金样本失败: {e}")
            return 0
    
    def add_history_records(self, records: List[Dict[str, Any]]) -> int:
        """
        添加历史资料到知识库
        
        Args:
            records: 历史记录列表，每个记录包含:
                - id: 唯一标识
                - title: 标题
                - content: 内容
                - period: 时期/年代
                - source: 来源
                - keywords: 关键词列表
        
        Returns:
            成功添加的记录数量
        """
        if not records:
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for record in records:
            record_id = record.get('id')
            if not record_id:
                logger.warning(f"历史记录缺少ID，跳过: {record}")
                continue
            
            existing = self.history_collection.get(ids=[record_id])
            if existing and existing['ids']:
                logger.warning(f"历史记录ID已存在，跳过: {record_id}")
                continue
            
            ids.append(record_id)
            documents.append(record.get('content', ''))
            
            metadata = {
                'title': record.get('title', ''),
                'period': record.get('period', ''),
                'source': record.get('source', ''),
                'keywords': ','.join(record.get('keywords', [])),
                'created_at': datetime.now().isoformat()
            }
            metadatas.append(metadata)
        
        if ids:
            try:
                self.history_collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(f"成功添加 {len(ids)} 条历史资料")
                return len(ids)
            except Exception as e:
                logger.error(f"添加历史资料失败: {e}")
                raise KnowledgeBaseError(
                    message="添加历史资料失败",
                    details=str(e)
                )
        
        return 0
    
    def search_history(
        self,
        query: str,
        k: int = None
    ) -> List[Dict[str, Any]]:
        """
        检索相似的历史资料
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认使用配置值
        
        Returns:
            相似历史记录列表
        """
        if k is None:
            k = settings.MAX_HISTORY_RESULTS
        
        try:
            results = self.history_collection.query(
                query_texts=[query],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            records = []
            if results and results['ids'] and results['ids'][0]:
                for i, record_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = max(0, 1 - distance)
                    
                    metadata = results['metadatas'][0][i]
                    
                    record = {
                        'id': record_id,
                        'title': metadata.get('title', ''),
                        'content': results['documents'][0][i],
                        'period': metadata.get('period', ''),
                        'source': metadata.get('source', ''),
                        'keywords': metadata.get('keywords', '').split(',') if metadata.get('keywords') else [],
                        'similarity': round(similarity, 4)
                    }
                    records.append(record)
            
            logger.info(f"检索到 {len(records)} 条相关历史资料")
            return records
            
        except Exception as e:
            logger.error(f"历史资料检索失败: {e}")
            raise KnowledgeBaseError(
                message="历史资料检索失败",
                details=str(e)
            )
    
    def get_history_stats(self) -> Dict[str, Any]:
        """
        获取历史资料库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            return {
                'total_cards': self.collection.count(),
                'golden_samples': self.golden_collection.count(),
                'history_records': self.history_collection.count(),
                'collection_name': settings.COLLECTION_NAME,
                'history_collection_name': settings.HISTORY_COLLECTION,
                'persist_directory': str(settings.get_chroma_path())
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}


# 全局知识库实例
_knowledge_base: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    """
    获取全局知识库实例
    
    Returns:
        知识库实例
    """
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base
