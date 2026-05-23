"""
嵌入模型模块
加载和管理本地嵌入模型，提供文本嵌入功能
"""
import os
import hashlib
import numpy as np
from typing import Optional, List, Union
from functools import lru_cache

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

from logger import get_logger
from config import settings
from exceptions import (
    EmbeddingError,
    ModelLoadError,
    EmbeddingGenerationError,
    InvalidInputError
)

logger = get_logger(__name__)


class SimpleEmbedding:
    """简单的文本嵌入实现（用于没有 sentence-transformers 的情况）"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """使用哈希函数生成简单的嵌入向量"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            hash_bytes = hashlib.sha256(text.encode('utf-8')).digest()
            np.random.seed(int.from_bytes(hash_bytes[:4], 'big'))
            embedding = np.random.randn(self.dimension).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        
        return np.array(embeddings)


class EmbeddingModel:
    """
    嵌入模型管理类
    
    使用单例模式确保模型只加载一次
    支持批量嵌入和缓存
    """
    
    _instance: Optional['EmbeddingModel'] = None
    _model: Optional[SentenceTransformer] = None
    _simple_model: Optional[SimpleEmbedding] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'EmbeddingModel':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化嵌入模型"""
        if self._initialized:
            return
        
        try:
            if HAS_SENTENCE_TRANSFORMERS:
                model_name = getattr(settings, 'EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
                logger.info(f"加载嵌入模型: {model_name}")
                self._model = SentenceTransformer(model_name)
                logger.info("嵌入模型加载成功")
            else:
                logger.warning("sentence-transformers 未安装，使用简单嵌入模式")
                self._simple_model = SimpleEmbedding()
        except Exception as e:
            logger.warning(f"嵌入模型加载失败，使用简单嵌入模式: {e}")
            self._simple_model = SimpleEmbedding()
        
        self._initialized = True
    
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        生成文本嵌入
        
        Args:
            texts: 单个文本或文本列表
            **kwargs: 传递给编码器的额外参数
            
        Returns:
            嵌入向量数组
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            if self._model is not None:
                return self._model.encode(texts, **kwargs)
            elif self._simple_model is not None:
                return self._simple_model.encode(texts, **kwargs)
            else:
                raise EmbeddingError("嵌入模型未初始化")
        except Exception as e:
            logger.error(f"嵌入生成失败: {e}")
            raise EmbeddingGenerationError(f"嵌入生成失败: {e}")
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入维度"""
        if self._model is not None:
            return self._model.get_sentence_embedding_dimension()
        return 384


@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    """获取嵌入模型单例"""
    return EmbeddingModel()


def get_embeddings(texts: List[str], normalize: bool = True) -> List[List[float]]:
    """
    获取文本的嵌入向量
    
    Args:
        texts: 文本列表
        normalize: 是否归一化向量
        
    Returns:
        嵌入向量列表
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize=normalize)
    
    if isinstance(embeddings, np.ndarray):
        return embeddings.tolist()
    return embeddings
