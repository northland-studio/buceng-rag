"""
工具函数模块测试
"""
import pytest
from utils import (
    validate_input,
    clean_event_text,
    parse_references,
    truncate_text,
    highlight_references
)
from exceptions import InvalidInputError, InputTooLongError


class TestValidateInput:
    """输入验证测试"""
    
    def test_valid_input(self):
        """测试有效输入"""
        text = "这是一个正常的输入"
        result = validate_input(text)
        assert result == text
    
    def test_strip_whitespace(self):
        """测试去除空白"""
        text = "  这是一个正常的输入  "
        result = validate_input(text)
        assert result == "这是一个正常的输入"
    
    def test_empty_input(self):
        """测试空输入"""
        with pytest.raises(InvalidInputError):
            validate_input("")
    
    def test_whitespace_only(self):
        """测试仅空白字符"""
        with pytest.raises(InvalidInputError):
            validate_input("   ")
    
    def test_too_long_input(self):
        """测试超长输入"""
        long_text = "a" * 6000
        with pytest.raises(InputTooLongError):
            validate_input(long_text, max_length=5000)
    
    def test_custom_max_length(self):
        """测试自定义最大长度"""
        text = "a" * 100
        result = validate_input(text, max_length=200)
        assert result == text
    
    def test_non_string_input(self):
        """测试非字符串输入"""
        with pytest.raises(InvalidInputError):
            validate_input(123)


class TestCleanEventText:
    """文本清洗测试"""
    
    def test_remove_extra_whitespace(self):
        """测试去除多余空白"""
        text = "这是  一个  测试"
        result = clean_event_text(text)
        assert result == "这是 一个 测试"
    
    def test_remove_extra_newlines(self):
        """测试去除多余换行"""
        text = "第一行\n\n\n\n第二行"
        result = clean_event_text(text)
        assert result == "第一行\n\n第二行"
    
    def test_strip(self):
        """测试去除首尾空白"""
        text = "  测试文本  "
        result = clean_event_text(text)
        assert result == "测试文本"


class TestParseReferences:
    """引用解析测试"""
    
    def test_parse_standard_format(self):
        """测试标准格式"""
        text = "根据[引用: theory_001]理论分析"
        refs = parse_references(text)
        assert "theory_001" in refs
    
    def test_parse_chinese_bracket(self):
        """测试中文括号格式"""
        text = "根据【引用: theory_002】理论分析"
        refs = parse_references(text)
        assert "theory_002" in refs
    
    def test_parse_multiple_references(self):
        """测试多个引用"""
        text = "根据[引用: theory_001]和[引用: theory_002]分析"
        refs = parse_references(text)
        assert len(refs) == 2
        assert "theory_001" in refs
        assert "theory_002" in refs
    
    def test_parse_no_references(self):
        """测试无引用"""
        text = "这段文本没有引用"
        refs = parse_references(text)
        assert len(refs) == 0
    
    def test_parse_deduplicate(self):
        """测试去重"""
        text = "根据[引用: theory_001]和[引用: theory_001]分析"
        refs = parse_references(text)
        assert len(refs) == 1


class TestTruncateText:
    """文本截断测试"""
    
    def test_short_text(self):
        """测试短文本"""
        text = "短文本"
        result = truncate_text(text, max_length=100)
        assert result == text
    
    def test_long_text(self):
        """测试长文本"""
        text = "a" * 100
        result = truncate_text(text, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")
    
    def test_custom_suffix(self):
        """测试自定义后缀"""
        text = "a" * 100
        result = truncate_text(text, max_length=50, suffix="...")
        assert result.endswith("...")


class TestHighlightReferences:
    """引用高亮测试"""
    
    def test_highlight_single(self):
        """测试单个引用高亮"""
        text = "根据[引用: theory_001]分析"
        refs = ["theory_001"]
        result = highlight_references(text, refs)
        assert "**[引用: theory_001]**" in result
    
    def test_highlight_multiple(self):
        """测试多个引用高亮"""
        text = "根据[引用: theory_001]和[引用: theory_002]分析"
        refs = ["theory_001", "theory_002"]
        result = highlight_references(text, refs)
        assert "**[引用: theory_001]**" in result
        assert "**[引用: theory_002]**" in result
    
    def test_no_highlight(self):
        """测试无引用"""
        text = "这段文本没有引用"
        refs = []
        result = highlight_references(text, refs)
        assert result == text
