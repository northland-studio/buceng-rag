"""
自定义异常模块
定义项目中使用的所有自定义异常类
"""
from typing import Optional, Any


class BaseAppException(Exception):
    """
    应用基础异常类
    
    所有自定义异常都应继承此类
    """
    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.details = details
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - 详情: {self.details}"
        return self.message
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于API响应"""
        result = {
            "error": self.message,
            "type": self.__class__.__name__
        }
        if self.details:
            result["details"] = self.details
        if self.error_code:
            result["error_code"] = self.error_code
        return result


# ============ 配置相关异常 ============

class ConfigurationError(BaseAppException):
    """配置错误异常"""
    def __init__(
        self,
        message: str = "配置错误",
        details: Optional[str] = None
    ):
        super().__init__(message, details, error_code="CONFIG_ERROR")


class MissingConfigError(ConfigurationError):
    """缺少必要配置异常"""
    def __init__(self, config_name: str):
        super().__init__(
            message=f"缺少必要配置: {config_name}",
            details=f"请在 .env 文件中设置 {config_name}",
            error_code="MISSING_CONFIG"
        )


# ============ 嵌入模型相关异常 ============

class EmbeddingError(BaseAppException):
    """嵌入模型异常"""
    def __init__(
        self,
        message: str = "嵌入模型错误",
        details: Optional[str] = None,
        error_code: Optional[str] = "EMBEDDING_ERROR"
    ):
        super().__init__(message, details, error_code=error_code)


class ModelLoadError(EmbeddingError):
    """模型加载失败异常"""
    def __init__(self, model_name: str, details: Optional[str] = None):
        super().__init__(
            message=f"模型加载失败: {model_name}",
            details=details,
            error_code="MODEL_LOAD_ERROR"
        )


class EmbeddingGenerationError(EmbeddingError):
    """嵌入生成失败异常"""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="嵌入向量生成失败",
            details=details,
            error_code="EMBEDDING_GENERATION_ERROR"
        )


# ============ 知识库相关异常 ============

class KnowledgeBaseError(BaseAppException):
    """知识库异常"""
    def __init__(
        self,
        message: str = "知识库错误",
        details: Optional[str] = None,
        error_code: Optional[str] = "KNOWLEDGE_BASE_ERROR"
    ):
        super().__init__(message, details, error_code=error_code)


class CollectionNotFoundError(KnowledgeBaseError):
    """集合不存在异常"""
    def __init__(self, collection_name: str):
        super().__init__(
            message=f"集合不存在: {collection_name}",
            error_code="COLLECTION_NOT_FOUND"
        )


class CardNotFoundError(KnowledgeBaseError):
    """卡片不存在异常"""
    def __init__(self, card_id: str):
        super().__init__(
            message=f"理论卡片不存在: {card_id}",
            error_code="CARD_NOT_FOUND"
        )


class DuplicateCardError(KnowledgeBaseError):
    """卡片重复异常"""
    def __init__(self, card_id: str):
        super().__init__(
            message=f"理论卡片已存在: {card_id}",
            error_code="DUPLICATE_CARD"
        )


# ============ LLM相关异常 ============

class LLMError(BaseAppException):
    """LLM调用异常"""
    def __init__(
        self,
        message: str = "LLM调用错误",
        details: Optional[str] = None,
        error_code: Optional[str] = "LLM_ERROR"
    ):
        super().__init__(message, details, error_code=error_code)


class APIConnectionError(LLMError):
    """API连接失败异常"""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="API连接失败",
            details=details,
            error_code="API_CONNECTION_ERROR"
        )


class APIResponseError(LLMError):
    """API响应错误异常"""
    def __init__(self, status_code: int, details: Optional[str] = None):
        super().__init__(
            message=f"API响应错误 (状态码: {status_code})",
            details=details,
            error_code="API_RESPONSE_ERROR"
        )


class APITimeoutError(LLMError):
    """API超时异常"""
    def __init__(self, timeout: int):
        super().__init__(
            message=f"API调用超时 ({timeout}秒)",
            error_code="API_TIMEOUT_ERROR"
        )


class RateLimitError(LLMError):
    """API速率限制异常"""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="API调用达到速率限制",
            details=details,
            error_code="RATE_LIMIT_ERROR"
        )


# ============ 数据验证相关异常 ============

class ValidationError(BaseAppException):
    """数据验证异常"""
    def __init__(
        self,
        message: str = "数据验证失败",
        details: Optional[str] = None,
        error_code: Optional[str] = "VALIDATION_ERROR"
    ):
        super().__init__(message, details, error_code=error_code)


class InputTooLongError(ValidationError):
    """输入过长异常"""
    def __init__(self, length: int, max_length: int):
        super().__init__(
            message=f"输入长度超出限制",
            details=f"当前长度: {length}, 最大长度: {max_length}",
            error_code="INPUT_TOO_LONG"
        )


class InvalidInputError(ValidationError):
    """无效输入异常"""
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"无效输入: {field}",
            details=reason,
            error_code="INVALID_INPUT"
        )


# ============ 文件操作相关异常 ============

class FileOperationError(BaseAppException):
    """文件操作异常"""
    def __init__(
        self,
        message: str = "文件操作错误",
        details: Optional[str] = None,
        error_code: Optional[str] = "FILE_OPERATION_ERROR"
    ):
        super().__init__(message, details, error_code=error_code)


class FileNotFoundError(FileOperationError):
    """文件不存在异常"""
    def __init__(self, file_path: str):
        super().__init__(
            message=f"文件不存在: {file_path}",
            error_code="FILE_NOT_FOUND"
        )


class FileParseError(FileOperationError):
    """文件解析失败异常"""
    def __init__(self, file_path: str, details: Optional[str] = None):
        super().__init__(
            message=f"文件解析失败: {file_path}",
            details=details,
            error_code="FILE_PARSE_ERROR"
        )
