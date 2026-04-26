"""
AI分析模块
使用LLM自动分析文档内容并提取关键信息
"""
from typing import List, Dict, Any, Optional
import json
import re

from logger import get_logger
from config import settings
from exceptions import LLMError
import llm_api

logger = get_logger(__name__)


# AI分析提示词
ANALYSIS_PROMPT = """你是一位专业的知识管理助手。你的任务是分析给定的文本内容，提取关键信息，并将其组织成结构化的知识卡片。

请分析以下文本内容，完成以下任务：

1. **内容摘要**: 用1-2句话概括文本的核心内容
2. **关键概念**: 提取文本中的关键概念和术语（3-5个）
3. **主题分类**: 判断文本属于哪个主题领域（如：社会学、经济学、心理学、管理学等）
4. **理论提取**: 如果文本包含理论观点或方法，请提取并说明
5. **应用场景**: 说明这个知识可以应用在哪些场景

请以JSON格式输出结果，格式如下：
```json
{
    "summary": "内容摘要",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "category": "主题分类",
    "theory": "理论观点（如果有）",
    "applications": ["应用场景1", "应用场景2"]
}
```

文本内容：
{text}
"""

CARD_GENERATION_PROMPT = """你是一位专业的知识管理助手。请根据分析结果，生成一张完整的知识卡片。

分析结果：
{analysis_result}

请生成一张知识卡片，包含以下字段：
- id: 唯一标识符（使用英文和下划线）
- title: 简洁明确的标题
- content: 详细的内容描述（200-500字）
- keywords: 关键词列表（3-5个）
- source: 来源信息

请以JSON格式输出：
```json
{
    "id": "card_id",
    "title": "卡片标题",
    "content": "卡片内容",
    "keywords": ["关键词1", "关键词2"],
    "source": "来源"
}
```
"""


class AIDocumentAnalyzer:
    """AI文档分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.llm_client = llm_api.get_llm_client()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        分析文本内容
        
        Args:
            text: 文本内容
        
        Returns:
            分析结果字典
        """
        try:
            # 限制文本长度
            if len(text) > 2000:
                text = text[:2000] + "..."
            
            # 构建提示词
            prompt = ANALYSIS_PROMPT.format(text=text)
            
            # 调用LLM
            messages = [
                {"role": "system", "content": "你是一位专业的知识管理助手，擅长分析和提取文本中的关键信息。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_client.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            
            # 提取JSON
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result_text)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                # 如果没有找到JSON块，尝试直接解析
                result = json.loads(result_text)
            
            logger.info(f"文本分析完成: {result.get('summary', 'N/A')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            # 返回默认结果
            return {
                "summary": "分析失败",
                "keywords": [],
                "category": "未分类",
                "theory": "",
                "applications": []
            }
        except Exception as e:
            logger.error(f"文本分析失败: {e}")
            raise LLMError(f"文本分析失败: {e}")
    
    def generate_knowledge_card(
        self,
        text: str,
        analysis_result: Dict[str, Any],
        source_name: str
    ) -> Dict[str, Any]:
        """
        生成知识卡片
        
        Args:
            text: 原始文本
            analysis_result: 分析结果
            source_name: 来源名称
        
        Returns:
            知识卡片字典
        """
        try:
            # 构建提示词
            prompt = CARD_GENERATION_PROMPT.format(
                analysis_result=json.dumps(analysis_result, ensure_ascii=False, indent=2)
            )
            
            # 调用LLM
            messages = [
                {"role": "system", "content": "你是一位专业的知识管理助手，擅长生成结构化的知识卡片。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_client.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            
            # 提取JSON
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result_text)
            if json_match:
                card = json.loads(json_match.group(1))
            else:
                card = json.loads(result_text)
            
            # 确保必要字段存在
            if 'id' not in card:
                card['id'] = f"{source_name}_auto_{hash(text) % 10000}"
            if 'source' not in card:
                card['source'] = source_name
            
            logger.info(f"知识卡片生成完成: {card.get('title', 'N/A')}")
            return card
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            # 返回默认卡片
            return {
                'id': f"{source_name}_auto_{hash(text) % 10000}",
                'title': f"{source_name} - 自动生成",
                'content': text[:500],
                'keywords': analysis_result.get('keywords', []),
                'source': source_name
            }
        except Exception as e:
            logger.error(f"知识卡片生成失败: {e}")
            raise LLMError(f"知识卡片生成失败: {e}")
    
    def analyze_and_generate_cards(
        self,
        text: str,
        source_name: str,
        chunk_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        分析文本并生成知识卡片
        
        Args:
            text: 文本内容
            source_name: 来源名称
            chunk_size: 文本块大小
        
        Returns:
            知识卡片列表
        """
        from document_processor import DocumentProcessor
        
        # 分割文本
        chunks = DocumentProcessor.split_text_into_chunks(text, chunk_size)
        
        logger.info(f"文本分割完成，共{len(chunks)}块")
        
        # 如果没有分割出文本块，将整个文本作为一个块
        if not chunks:
            logger.warning("文本分割未产生文本块，将整个文本作为一个块处理")
            chunks = [text]
        
        cards = []
        failed_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                logger.info(f"正在处理文本块 {i+1}/{len(chunks)}")
                
                # 分析文本块
                analysis = self.analyze_text(chunk)
                
                # 生成卡片
                card = self.generate_knowledge_card(chunk, analysis, f"{source_name}_part{i+1}")
                
                cards.append(card)
                logger.info(f"文本块 {i+1} 处理成功")
                
            except Exception as e:
                logger.error(f"处理文本块 {i+1} 失败: {e}")
                failed_chunks.append((i, chunk, str(e)))
                # 不跳过，继续处理下一个块
                continue
        
        # 如果所有AI分析都失败了，使用简单方法生成卡片
        if not cards and failed_chunks:
            logger.warning("所有AI分析都失败，使用简单方法生成卡片")
            for i, chunk, error in failed_chunks:
                # 生成基本卡片
                card = {
                    'id': f"{source_name}_simple_{i+1}",
                    'title': f"{source_name} - 片段 {i+1}",
                    'content': chunk[:500] if len(chunk) > 500 else chunk,
                    'keywords': [],
                    'source': source_name
                }
                cards.append(card)
                logger.info(f"为文本块 {i+1} 生成基本卡片")
        
        logger.info(f"成功生成 {len(cards)} 张知识卡片")
        return cards


def analyze_document_with_ai(text: str, source_name: str) -> List[Dict[str, Any]]:
    """
    使用AI分析文档并生成知识卡片
    
    Args:
        text: 文档文本
        source_name: 来源名称
    
    Returns:
        知识卡片列表
    """
    analyzer = AIDocumentAnalyzer()
    return analyzer.analyze_and_generate_cards(text, source_name)
