"""
处理玄剑公会通史文档，提取历史卡片并导入历史资料库
使用zipfile直接读取docx内容，避免大文件解析问题
"""
import json
import sys
import os
import re
import zipfile
from xml.etree import ElementTree as ET
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger, get_logger
import knowledge_base

setup_logger()
logger = get_logger(__name__)


def extract_text_from_docx_robust(file_path: str) -> str:
    """
    使用zipfile直接读取docx内容，避免大文件解析问题
    
    Args:
        file_path: DOCX文件路径
    
    Returns:
        提取的文本内容
    """
    try:
        text_parts = []
        
        with zipfile.ZipFile(file_path, 'r') as z:
            if 'word/document.xml' in z.namelist():
                with z.open('word/document.xml') as f:
                    content = f.read()
                    
                    tree = ET.fromstring(content)
                    
                    namespaces = {
                        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                    }
                    
                    for paragraph in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                        para_text = ''
                        for text_elem in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                            if text_elem.text:
                                para_text += text_elem.text
                        if para_text.strip():
                            text_parts.append(para_text)
        
        text = '\n'.join(text_parts)
        logger.info(f"成功从DOCX提取文本: {file_path}, 共{len(text)}字符")
        return text
        
    except Exception as e:
        logger.error(f"DOCX文本提取失败: {e}")
        raise


def extract_history_cards_from_text(text: str, source_name: str) -> list:
    """
    从文本中提取历史事件卡片
    
    Args:
        text: 文档文本
        source_name: 来源名称
    
    Returns:
        历史卡片列表
    """
    cards = []
    
    paragraphs = re.split(r'\n+', text)
    
    card_id = 1
    current_para = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        if len(para) < 30:
            current_para += para
            continue
        
        if current_para:
            para = current_para + para
            current_para = ""
        
        if len(para) < 50:
            continue
        
        title_match = re.match(r'^[第\d一二三四五六七八九十百千]+[章节篇部]', para)
        if title_match:
            continue
        
        if len(para) > 100:
            title = para[:50] + "..."
        else:
            title = para[:50] if len(para) > 20 else f"历史事件{card_id}"
        
        title = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：""''（）【】]', '', title)
        
        keywords = []
        keyword_patterns = [
            r'公会', r'玩家', r'服务器', r'联盟', r'战争', r'和平',
            r'建立', r'解散', r'合并', r'分裂', r'改革', r'发展',
            r'资源', r'领土', r'经济', r'政治', r'外交', r'军事',
            r'管理', r'制度', r'规则', r'领袖', r'成员', r'组织'
        ]
        
        for pattern in keyword_patterns:
            if re.search(pattern, para):
                keywords.append(pattern.replace('\\', ''))
        
        keywords = list(set(keywords))[:5]
        
        period = "玄剑公会历史"
        
        date_match = re.search(r'(\d{4}年|\d{1,2}月\d{1,2}日|\d{4}年\d{1,2}月)', para)
        if date_match:
            period = date_match.group(1)
        
        card = {
            'id': f'xuanjian_history_{card_id:03d}',
            'title': title,
            'content': para,
            'period': period,
            'source': source_name,
            'keywords': keywords
        }
        
        cards.append(card)
        card_id += 1
    
    return cards


def process_xuanjian_history():
    """处理玄剑公会通史文档"""
    doc_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '玄剑公会公会通史0517.docx'
    )
    
    if not os.path.exists(doc_path):
        logger.error(f"文档不存在: {doc_path}")
        return 0
    
    logger.info(f"正在处理文档: {doc_path}")
    
    text = extract_text_from_docx_robust(doc_path)
    
    if not text:
        logger.error("无法提取文档文本")
        return 0
    
    logger.info(f"提取到文本长度: {len(text)} 字符")
    
    cards = extract_history_cards_from_text(text, "玄剑公会通史")
    
    logger.info(f"提取到 {len(cards)} 条历史卡片")
    
    if cards:
        kb = knowledge_base.get_knowledge_base()
        count = kb.add_history_records(cards)
        
        logger.info(f"成功导入 {count} 条玄剑公会历史资料")
        
        stats = kb.get_history_stats()
        logger.info(f"知识库当前统计: {stats}")
        
        return count
    
    return 0


if __name__ == "__main__":
    process_xuanjian_history()
