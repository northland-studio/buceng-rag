"""
工具函数模块
提供输入验证、文本处理、引用解析等工具函数
"""
import re
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from logger import get_logger
from config import settings
from exceptions import (
    ValidationError,
    InputTooLongError,
    InvalidInputError,
    FileOperationError
)

logger = get_logger(__name__)


def validate_input(
    text: str,
    max_length: Optional[int] = None,
    field_name: str = "输入"
) -> str:
    """
    验证并清洗输入文本
    
    Args:
        text: 输入文本
        max_length: 最大长度，默认使用配置值
        field_name: 字段名称（用于错误消息）
    
    Returns:
        清洗后的文本
    
    Raises:
        InvalidInputError: 输入无效
        InputTooLongError: 输入过长
    """
    if max_length is None:
        max_length = settings.MAX_INPUT_LENGTH
    
    # 类型检查
    if not isinstance(text, str):
        raise InvalidInputError(
            field=field_name,
            reason="输入必须是字符串"
        )
    
    # 去除首尾空白
    text = text.strip()
    
    # 空值检查
    if len(text) == 0:
        raise InvalidInputError(
            field=field_name,
            reason="输入不能为空"
        )
    
    # 长度检查
    if len(text) > max_length:
        raise InputTooLongError(
            length=len(text),
            max_length=max_length
        )
    
    return text


def clean_event_text(text: str) -> str:
    """
    清洗事件文本
    
    Args:
        text: 原始文本
    
    Returns:
        清洗后的文本
    """
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空白
    text = text.strip()
    
    # 去除多余的换行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text


def parse_references(analysis_text: str) -> List[str]:
    """
    提取分析文本中的引用ID
    
    支持格式：
    - [引用: theory_id]
    - [引用:theory_id]
    - 【引用: theory_id】
    
    Args:
        analysis_text: 分析文本
    
    Returns:
        引用ID列表（去重）
    """
    # 匹配引用模式
    pattern = r'[【\[引用:\s*([^\]】]+)[\]】]'
    matches = re.findall(pattern, analysis_text)
    
    # 去重并清理
    references = list(set(match.strip() for match in matches))
    
    logger.debug(f"从分析文本中提取到 {len(references)} 个引用")
    
    return references


def format_card_for_display(card: Dict[str, Any]) -> str:
    """
    格式化理论卡片用于显示
    
    Args:
        card: 卡片信息字典
    
    Returns:
        格式化后的文本
    """
    text = f"### {card['title']}\n\n"
    text += f"**ID**: {card['id']}\n\n"
    text += f"**内容**: {card['content']}\n\n"
    text += f"**来源**: {card['source']}\n\n"
    
    if card.get('keywords'):
        text += f"**关键词**: {', '.join(card['keywords'])}\n\n"
    
    if card.get('similarity'):
        text += f"**相似度**: {card['similarity']:.2%}\n\n"
    
    return text


def save_golden_sample(
    event: str,
    analysis: str,
    rating: int,
    retrieved_cards: Optional[List[str]] = None,
    file_path: Optional[str] = None
) -> bool:
    """
    保存黄金样本到JSONL文件
    
    Args:
        event: 事件文本
        analysis: 分析结果
        rating: 评分 (1-3)
        retrieved_cards: 检索到的卡片ID列表
        file_path: 保存路径，默认使用配置值
    
    Returns:
        是否保存成功
    
    Raises:
        ValidationError: 评分无效
    """
    # 验证评分
    if rating not in [1, 2, 3]:
        raise ValidationError(
            message="评分必须在1-3之间",
            details=f"当前评分: {rating}"
        )
    
    # 使用默认路径
    if file_path is None:
        file_path = settings.get_data_path(settings.GOLDEN_SAMPLES_FILE)
    
    try:
        # 准备样本数据
        sample = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "analysis": analysis,
            "rating": rating,
            "retrieved_cards": retrieved_cards or []
        }
        
        # 确保目录存在
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 追加写入
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        logger.info(f"黄金样本已保存: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存黄金样本失败: {e}")
        return False


def load_json_file(file_path: str) -> Any:
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        JSON数据
    
    Raises:
        FileOperationError: 文件操作失败
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise FileOperationError(
                message=f"文件不存在: {file_path}"
            )
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"成功加载JSON文件: {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise FileOperationError(
            message=f"JSON文件解析失败: {file_path}",
            details=str(e)
        )
    except Exception as e:
        logger.error(f"加载文件失败: {e}")
        raise FileOperationError(
            message=f"加载文件失败: {file_path}",
            details=str(e)
        )


def save_json_file(
    data: Any,
    file_path: str,
    indent: int = 2
) -> bool:
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        indent: 缩进空格数
    
    Returns:
        是否保存成功
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        logger.info(f"成功保存JSON文件: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存JSON文件失败: {e}")
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def highlight_references(text: str, references: List[str]) -> str:
    """
    高亮显示引用部分
    
    Args:
        text: 原始文本
        references: 引用ID列表
    
    Returns:
        处理后的文本（Markdown格式）
    """
    for ref_id in references:
        # 匹配引用模式
        pattern = rf'(\[引用:\s*{re.escape(ref_id)}\])'
        replacement = r'**\1**'
        text = re.sub(pattern, replacement, text)
    
    return text


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    简单的关键词提取（基于词频）
    
    注意：这是一个简单的实现，实际应用中应使用专业的关键词提取算法
    
    Args:
        text: 文本内容
        max_keywords: 最大关键词数
    
    Returns:
        关键词列表
    """
    # 中文分词（简单实现，按字符分割）
    # 实际应用中应使用jieba等专业分词工具
    words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
    
    # 统计词频
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # 排序并取前N个
    sorted_words = sorted(
        word_freq.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [word for word, freq in sorted_words[:max_keywords]]


def format_timestamp(timestamp: str) -> str:
    """
    格式化时间戳
    
    Args:
        timestamp: ISO格式时间戳
    
    Returns:
        格式化后的时间字符串
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return timestamp


def calculate_reading_time(text: str, chars_per_minute: int = 500) -> int:
    """
    计算阅读时间（分钟）
    
    Args:
        text: 文本内容
        chars_per_minute: 每分钟阅读字数
    
    Returns:
        阅读时间（分钟）
    """
    char_count = len(text)
    minutes = max(1, char_count // chars_per_minute)
    return minutes
