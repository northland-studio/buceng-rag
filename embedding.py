"""
嵌入模型模块
加载和管理本地嵌入模型，提供文本嵌入功能
"""
import os
from typing import Optional, List, Union
from sentence_transformers import SentenceTransformer
import numpy as np
from functools import lru_cache

from logger import get_logger
from config import settings
from exceptions import (
    EmbeddingError,
    ModelLoadError,
    EmbeddingGenerationError,
    InvalidInputError
)

logger = get_logger(__name__)


class EmbeddingModel:
    """
    嵌入模型管理类
    
    使用单例模式确保模型只加载一次
    支持批量嵌入和缓存
    """
    
    _instance: Optional['EmbeddingModel'] = None
    _model: Optional[SentenceTransformer] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'EmbeddingModel':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self) -> None:
        """
        初始化嵌入模型
        
        Raises:
            ModelLoadError: 模型加载失败
        """
        if self._initialized:
            return
        
        try:
            # 设置Hugging Face镜像源（如果配置了）
            if settings.HF_ENDPOINT:
                os.environ['HF_ENDPOINT'] = settings.HF_ENDPOINT
                logger.info(f"使用Hugging Face镜像源: {settings.HF_ENDPOINT}")
            
            logger.info(f"正在加载嵌入模型: {settings.EMBEDDING_MODEL_NAME}")
            logger.info(f"运行设备: {settings.EMBEDDING_DEVICE}")
            
            self._model = SentenceTransformer(
                settings.EMBEDDING_MODEL_NAME,
                device=settings.EMBEDDING_DEVICE
            )
            
            # 获取模型信息
            embedding_dim = self._model.get_sentence_embedding_dimension()
            logger.info(f"嵌入模型加载成功，向量维度: {embedding_dim}")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            raise ModelLoadError(
                model_name=settings.EMBEDDING_MODEL_NAME,
                details=str(e)
            )
    
    @property
    def model(self) -> SentenceTransformer:
        """获取模型实例"""
        if not self._initialized:
            self.initialize()
        return self._model
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入向量维度"""
        return self.model.get_sentence_embedding_dimension()
    
    def get_embedding(
        self,
        text: str,
        normalize: bool = True
    ) -> List[float]:
        """
        获取单个文本的嵌入向量
        
        Args:
            text: 输入文本
            normalize: 是否归一化向量
        
        Returns:
            嵌入向量列表
        
        Raises:
            InvalidInputError: 输入无效
            EmbeddingGenerationError: 嵌入生成失败
        """
        # 输入验证
        if not text or not isinstance(text, str):
            raise InvalidInputError(
                field="text",
                reason="输入必须是非空字符串"
            )
        
        # 去除首尾空白
        text = text.strip()
        
        if len(text) == 0:
            raise InvalidInputError(
                field="text",
                reason="输入不能只包含空白字符"
            )
        
        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=normalize,
                convert_to_numpy=True
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"嵌入生成失败: {e}")
            raise EmbeddingGenerationError(details=str(e))
    
    def get_embeddings(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        批量获取文本的嵌入向量
        
        Args:
            texts: 文本列表
            normalize: 是否归一化向量
            show_progress: 是否显示进度条
        
        Returns:
            嵌入向量列表
        
        Raises:
            InvalidInputError: 输入无效
            EmbeddingGenerationError: 嵌入生成失败
        """
        # 输入验证
        if not texts or not isinstance(texts, list):
            raise InvalidInputError(
                field="texts",
                reason="输入必须是非空列表"
            )
        
        # 过滤空文本
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        
        if len(valid_texts) == 0:
            raise InvalidInputError(
                field="texts",
                reason="没有有效的文本输入"
            )
        
        try:
            # 自动显示进度条（当文本数量较多时）
            if show_progress or len(valid_texts) > 100:
                show_progress = True
            
            embeddings = self.model.encode(
                valid_texts,
                normalize_embeddings=normalize,
                convert_to_numpy=True,
                show_progress_bar=show_progress
            )
            
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"批量嵌入生成失败: {e}")
            raise EmbeddingGenerationError(details=str(e))
    
    def compute_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数 (0-1)
        """
        embeddings = self.get_embeddings([text1, text2], normalize=True)
        
        # 计算余弦相似度
        vec1 = np.array(embeddings[0])
        vec2 = np.array(embeddings[1])
        
        similarity = np.dot(vec1, vec2) / (
            np.linalg.norm(vec1) * np.linalg.norm(vec2)
        )
        
        return float(similarity)
    
    def is_initialized(self) -> bool:
        """检查模型是否已初始化"""
        return self._initialized


# 全局嵌入模型实例
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """
    获取全局嵌入模型实例
    
    Returns:
        嵌入模型实例
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model


def get_embedding(text: str, normalize: bool = True) -> List[float]:
    """
    获取文本嵌入向量（便捷函数）
    
    Args:
        text: 输入文本
        normalize: 是否归一化
    
    Returns:
        嵌入向量列表
    """
    model = get_embedding_model()
    return model.get_embedding(text, normalize)


def get_embeddings(
    texts: List[str],
    normalize: bool = True,
    show_progress: bool = False
) -> List[List[float]]:
    """
    批量获取文本嵌入向量（便捷函数）
    
    Args:
        texts: 文本列表
        normalize: 是否归一化
        show_progress: 是否显示进度
    
    Returns:
        嵌入向量列表
    """
    model = get_embedding_model()
    return model.get_embeddings(texts, normalize, show_progress)
