"""
异常模块测试
"""
import pytest
from exceptions import (
    BaseAppException,
    ConfigurationError,
    EmbeddingError,
    ModelLoadError,
    KnowledgeBaseError,
    CardNotFoundError,
    LLMError,
    ValidationError,
    InvalidInputError
)


class TestExceptions:
    """异常测试"""
    
    def test_base_exception(self):
        """测试基础异常"""
        exc = BaseAppException(
            message="测试异常",
            details="详细信息"
        )
        
        assert exc.message == "测试异常"
        assert exc.details == "详细信息"
        assert "测试异常" in str(exc)
        assert "详细信息" in str(exc)
    
    def test_exception_to_dict(self):
        """测试异常转字典"""
        exc = BaseAppException(
            message="测试异常",
            details="详细信息",
            error_code="TEST_ERROR"
        )
        
        result = exc.to_dict()
        
        assert result["error"] == "测试异常"
        assert result["details"] == "详细信息"
        assert result["error_code"] == "TEST_ERROR"
        assert result["type"] == "BaseAppException"
    
    def test_configuration_error(self):
        """测试配置异常"""
        exc = ConfigurationError(
            message="配置错误",
            details="缺少必要配置"
        )
        
        assert exc.message == "配置错误"
        assert exc.error_code == "CONFIG_ERROR"
    
    def test_model_load_error(self):
        """测试模型加载异常"""
        exc = ModelLoadError(
            model_name="test_model",
            details="文件不存在"
        )
        
        assert "test_model" in exc.message
        assert exc.error_code == "MODEL_LOAD_ERROR"
    
    def test_card_not_found_error(self):
        """测试卡片不存在异常"""
        exc = CardNotFoundError(card_id="test_id")
        
        assert "test_id" in exc.message
        assert exc.error_code == "CARD_NOT_FOUND"
    
    def test_invalid_input_error(self):
        """测试无效输入异常"""
        exc = InvalidInputError(
            field="test_field",
            reason="不能为空"
        )
        
        assert "test_field" in exc.message
        assert exc.error_code == "INVALID_INPUT"
    
    def test_exception_without_details(self):
        """测试无详细信息的异常"""
        exc = BaseAppException(message="测试异常")
        
        assert exc.message == "测试异常"
        assert exc.details is None
        assert str(exc) == "测试异常"
