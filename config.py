"""
配置管理模块
使用 pydantic-settings 进行配置管理和验证
"""
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """
    应用配置类
    
    从 .env 文件加载配置，支持类型验证和默认值
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = Field(
        ...,
        description="DeepSeek API密钥"
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API基础URL"
    )
    
    # 嵌入模型配置
    EMBEDDING_MODEL_NAME: str = Field(
        default="BAAI/bge-large-zh-v1.5",
        description="嵌入模型名称"
    )
    EMBEDDING_DEVICE: str = Field(
        default="cpu",
        description="嵌入模型运行设备 (cpu/cuda)"
    )
    HF_ENDPOINT: Optional[str] = Field(
        default=None,
        description="Hugging Face镜像源地址（国内推荐：https://hf-mirror.com）"
    )
    
    # ChromaDB 配置
    CHROMA_PERSIST_DIR: str = Field(
        default="./chroma_db",
        description="ChromaDB持久化目录"
    )
    COLLECTION_NAME: str = Field(
        default="sociology_cards",
        description="理论卡片集合名称"
    )
    GOLDEN_SAMPLES_COLLECTION: str = Field(
        default="golden_samples",
        description="黄金样本集合名称"
    )
    HISTORY_COLLECTION: str = Field(
        default="history_records",
        description="历史资料集合名称"
    )
    MAX_HISTORY_RESULTS: int = Field(
        default=5,
        description="历史资料检索返回的最大结果数"
    )
    
    # 应用配置
    MAX_INPUT_LENGTH: int = Field(
        default=5000,
        description="最大输入长度（字符）"
    )
    MAX_RETRIEVAL_RESULTS: int = Field(
        default=10,
        description="检索返回的最大结果数"
    )
    MAX_RETRIEVAL_LIMIT: int = Field(
        default=50,
        description="检索数量上限"
    )
    
    # LLM 配置
    LLM_MODEL: str = Field(
        default="deepseek-chat",
        description="LLM模型名称"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="LLM温度参数"
    )
    LLM_TIMEOUT: int = Field(
        default=60,
        ge=10,
        le=300,
        description="LLM调用超时时间（秒）"
    )
    LLM_THINKING_ENABLED: bool = Field(
        default=True,
        description="是否启用思考模式（DeepSeek V4）"
    )
    LLM_REASONING_EFFORT: str = Field(
        default="high",
        description="推理努力程度（low/medium/high）"
    )
    LLM_MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        le=10,
        description="LLM调用最大重试次数"
    )
    
    # 日志配置
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)"
    )
    LOG_DIR: str = Field(
        default="./logs",
        description="日志文件目录"
    )
    
    # 数据配置
    DATA_DIR: str = Field(
        default="./data",
        description="数据文件目录"
    )
    SEED_CARDS_FILE: str = Field(
        default="seed_cards.json",
        description="初始理论卡片文件名"
    )
    GOLDEN_SAMPLES_FILE: str = Field(
        default="golden_samples.jsonl",
        description="黄金样本文件名"
    )
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"日志级别必须是 {valid_levels} 之一")
        return v_upper
    
    @field_validator("EMBEDDING_DEVICE")
    @classmethod
    def validate_device(cls, v: str) -> str:
        """验证设备类型"""
        valid_devices = ["cpu", "cuda"]
        v_lower = v.lower()
        if v_lower not in valid_devices:
            raise ValueError(f"设备类型必须是 {valid_devices} 之一")
        return v_lower
    
    def get_data_path(self, filename: str) -> Path:
        """获取数据文件的完整路径"""
        return Path(self.DATA_DIR) / filename
    
    def get_log_path(self, filename: str) -> Path:
        """获取日志文件的完整路径"""
        return Path(self.LOG_DIR) / filename
    
    def get_chroma_path(self) -> Path:
        """获取ChromaDB的完整路径"""
        return Path(self.CHROMA_PERSIST_DIR)


# 全局配置实例
try:
    settings = Settings()
except Exception as e:
    print(f"配置加载失败: {e}")
    print("请确保 .env 文件存在并包含必要的配置项")
    print("可以复制 .env.example 为 .env 并填写配置")
    raise
