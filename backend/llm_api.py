"""
LLM API模块
调用DeepSeek API生成分析报告
"""
from typing import List, Dict, Optional, Generator, Any
from openai import OpenAI, APIError, APIConnectionError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from logger import get_logger
from config import settings
from exceptions import (
    LLMError,
    APIConnectionError as AppAPIConnectionError,
    APITimeoutError as AppAPITimeoutError,
    RateLimitError as AppRateLimitError,
    InvalidInputError
)

logger = get_logger(__name__)


# 系统提示模板
SYSTEM_PROMPT_MINECRAFT = """你是一位专注于Minecraft游戏社会学研究的专家。你的任务是基于提供的理论卡片和历史资料，对游戏内的事件进行深入的社会学分析。

分析要求：
1. 只能依据提供的参考理论进行分析，不要编造或使用未提供的理论
2. 如果提供了历史资料，应当结合历史背景进行分析，寻找相似的历史事件或现象
3. 分析应包含以下部分：
   - 事件概要：简要总结事件的核心内容
   - 理论分析：使用相关理论解释事件，每个理论引用需标注 [引用: 理论ID]
   - 历史参照：如有相关历史资料，分析当前事件与历史事件的异同
   - 引申问题：提出值得进一步探讨的问题

输出格式：
## 事件概要
[事件总结]

## 理论分析
### 1. [理论标题] [引用: 理论ID]
[理论应用分析]

### 2. [理论标题] [引用: 理论ID]
[理论应用分析]

## 历史参照
[如有历史资料，分析当前事件与历史事件的相似性和差异性]

## 引申问题
1. [问题1]
2. [问题2]
3. [问题3]

请确保分析严谨、逻辑清晰，理论引用准确。"""


SYSTEM_PROMPT_GENERAL = """你是一位资深的社会科学研究专家，精通马克思主义理论、社会学、政治学、经济学等多学科知识。你的任务是基于提供的理论卡片和历史资料，对现实社会现象进行深入的社会科学分析。

分析要求：
1. 只能依据提供的参考理论进行分析，不要编造或使用未提供的理论
2. 如果提供了历史资料，应当结合历史背景进行分析，寻找相似的历史事件或现象
3. 分析应包含以下部分：
   - 现象概要：简要总结社会现象的核心内容
   - 理论分析：使用相关理论解释现象，每个理论引用需标注 [引用: 理论ID]
   - 历史参照：如有相关历史资料，分析当前现象与历史事件的异同
   - 深度解读：结合理论进行深入剖析
   - 引申问题：提出值得进一步探讨的问题

输出格式：
## 现象概要
[现象总结]

## 理论分析
### 1. [理论标题] [引用: 理论ID]
[理论应用分析]

### 2. [理论标题] [引用: 理论ID]
[理论应用分析]

## 历史参照
[如有历史资料，分析当前现象与历史事件的相似性和差异性，揭示历史规律]

## 深度解读
[结合多个理论进行综合分析，揭示现象背后的深层机制]

## 引申问题
1. [问题1]
2. [问题2]
3. [问题3]

请确保分析严谨、逻辑清晰，理论引用准确，体现马克思主义立场观点方法。"""


SYSTEM_PROMPT = SYSTEM_PROMPT_MINECRAFT


class LLMClient:
    """
    LLM客户端类
    
    封装DeepSeek API调用，支持重试和流式输出
    """
    
    def __init__(self):
        """初始化LLM客户端"""
        self._client: Optional[OpenAI] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """
        初始化OpenAI客户端
        
        Raises:
            LLMError: 初始化失败
        """
        if self._initialized:
            return
        
        try:
            logger.info(f"初始化LLM客户端，API地址: {settings.DEEPSEEK_BASE_URL}")
            
            # 清除可能存在的代理环境变量，避免OpenAI库自动使用代理
            import os
            old_http_proxy = os.environ.get('HTTP_PROXY')
            old_https_proxy = os.environ.get('HTTPS_PROXY')
            old_http_proxy_lower = os.environ.get('http_proxy')
            old_https_proxy_lower = os.environ.get('https_proxy')
            
            # 临时移除代理设置
            for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                if key in os.environ:
                    del os.environ[key]
            
            try:
                self._client = OpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_BASE_URL,
                    timeout=settings.LLM_TIMEOUT
                )
                
                self._initialized = True
                logger.info("LLM客户端初始化成功")
            finally:
                # 恢复代理设置
                if old_http_proxy:
                    os.environ['HTTP_PROXY'] = old_http_proxy
                if old_https_proxy:
                    os.environ['HTTPS_PROXY'] = old_https_proxy
                if old_http_proxy_lower:
                    os.environ['http_proxy'] = old_http_proxy_lower
                if old_https_proxy_lower:
                    os.environ['https_proxy'] = old_https_proxy_lower
            
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            raise LLMError(
                message="LLM客户端初始化失败",
                details=str(e)
            )
    
    @property
    def client(self) -> OpenAI:
        """获取OpenAI客户端实例"""
        if not self._initialized:
            self.initialize()
        return self._client
    
    def _get_system_prompt(self, analysis_mode: str = "minecraft") -> str:
        """
        获取系统提示
        
        Args:
            analysis_mode: 分析模式 (minecraft/general)
        
        Returns:
            系统提示内容
        """
        if analysis_mode == "general":
            return SYSTEM_PROMPT_GENERAL
        return SYSTEM_PROMPT_MINECRAFT
    
    def _build_user_message(
        self,
        event_text: str,
        retrieved_cards: List[Dict[str, Any]],
        history_records: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        构建用户消息
        
        Args:
            event_text: 事件文本
            retrieved_cards: 检索到的理论卡片
            history_records: 检索到的历史资料
        
        Returns:
            用户消息内容
        """
        cards_text = "参考理论卡片：\n\n"
        for i, card in enumerate(retrieved_cards, 1):
            cards_text += f"### 理论 {i}: {card['title']} [ID: {card['id']}]\n"
            cards_text += f"内容：{card['content']}\n"
            cards_text += f"来源：{card['source']}\n"
            cards_text += f"关键词：{', '.join(card['keywords'])}\n\n"
        
        history_text = ""
        if history_records:
            history_text = "\n---\n\n相关历史资料：\n\n"
            for i, record in enumerate(history_records, 1):
                history_text += f"### 历史资料 {i}: {record['title']}\n"
                history_text += f"时期：{record.get('period', '未知')}\n"
                history_text += f"内容：{record['content']}\n"
                history_text += f"来源：{record['source']}\n\n"
        
        message = f"{cards_text}{history_text}\n---\n\n待分析事件：\n{event_text}"
        
        return message
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        reraise=True
    )
    def generate_analysis(
        self,
        event_text: str,
        retrieved_cards: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        analysis_mode: str = "minecraft",
        history_records: Optional[List[Dict[str, Any]]] = None,
        thinking_enabled: bool = True,
        reasoning_effort: str = "high"
    ) -> str:
        """
        生成分析报告（非流式）
        
        Args:
            event_text: 事件文本
            retrieved_cards: 检索到的理论卡片
            temperature: 温度参数，默认使用配置值
            analysis_mode: 分析模式 (minecraft/general)
            history_records: 检索到的历史资料
            thinking_enabled: 是否启用思考模式
            reasoning_effort: 推理努力程度
        
        Returns:
            分析报告文本
        
        Raises:
            InvalidInputError: 输入验证失败
            LLMError: LLM调用失败
        """
        if not event_text or not event_text.strip():
            raise InvalidInputError(
                field="event_text",
                reason="事件文本不能为空"
            )
        
        if len(event_text) > settings.MAX_INPUT_LENGTH:
            raise InvalidInputError(
                field="event_text",
                reason=f"事件文本长度超过限制({settings.MAX_INPUT_LENGTH}字符)"
            )
        
        if not retrieved_cards:
            logger.warning("没有检索到理论卡片，分析可能不够准确")
        
        try:
            user_message = self._build_user_message(event_text, retrieved_cards, history_records)
            system_prompt = self._get_system_prompt(analysis_mode)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            logger.info(f"调用LLM生成分析，模型: {settings.LLM_MODEL}, 模式: {analysis_mode}")
            
            api_params = {
                "model": settings.LLM_MODEL,
                "messages": messages,
                "temperature": temperature or settings.LLM_TEMPERATURE,
                "stream": False
            }
            
            if settings.LLM_MODEL.startswith("deepseek-v4") and thinking_enabled:
                api_params["extra_body"] = {"thinking": {"type": "enabled"}}
                api_params["reasoning_effort"] = reasoning_effort
            
            response = self.client.chat.completions.create(**api_params)
            
            analysis = response.choices[0].message.content
            
            if response.usage:
                logger.info(
                    f"LLM调用成功 - "
                    f"Prompt tokens: {response.usage.prompt_tokens}, "
                    f"Completion tokens: {response.usage.completion_tokens}, "
                    f"Total tokens: {response.usage.total_tokens}"
                )
            
            return analysis
            
        except APIConnectionError as e:
            logger.error(f"API连接失败: {e}")
            raise AppAPIConnectionError(details=str(e))
        
        except APITimeoutError as e:
            logger.error(f"API超时: {e}")
            raise AppAPITimeoutError(timeout=settings.LLM_TIMEOUT)
        
        except RateLimitError as e:
            logger.error(f"API速率限制: {e}")
            raise AppRateLimitError(details=str(e))
        
        except APIError as e:
            logger.error(f"API错误: {e}")
            raise LLMError(
                message="API调用失败",
                details=str(e)
            )
        
        except Exception as e:
            logger.error(f"生成分析失败: {e}")
            raise LLMError(
                message="生成分析失败",
                details=str(e)
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        reraise=True
    )
    def generate_analysis_stream(
        self,
        event_text: str,
        retrieved_cards: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        analysis_mode: str = "minecraft",
        history_records: Optional[List[Dict[str, Any]]] = None,
        thinking_enabled: bool = True,
        reasoning_effort: str = "high"
    ) -> Generator[str, None, None]:
        """
        生成分析报告（流式输出）
        
        Args:
            event_text: 事件文本
            retrieved_cards: 检索到的理论卡片
            temperature: 温度参数
            analysis_mode: 分析模式 (minecraft/general)
            history_records: 检索到的历史资料
            thinking_enabled: 是否启用思考模式
            reasoning_effort: 推理努力程度
        
        Yields:
            分析报告文本片段
        
        Raises:
            InvalidInputError: 输入验证失败
            LLMError: LLM调用失败
        """
        if not event_text or not event_text.strip():
            raise InvalidInputError(
                field="event_text",
                reason="事件文本不能为空"
            )
        
        if len(event_text) > settings.MAX_INPUT_LENGTH:
            raise InvalidInputError(
                field="event_text",
                reason=f"事件文本长度超过限制({settings.MAX_INPUT_LENGTH}字符)"
            )
        
        try:
            user_message = self._build_user_message(event_text, retrieved_cards, history_records)
            system_prompt = self._get_system_prompt(analysis_mode)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            logger.info(f"调用LLM生成分析（流式），模型: {settings.LLM_MODEL}, 模式: {analysis_mode}")
            
            api_params = {
                "model": settings.LLM_MODEL,
                "messages": messages,
                "temperature": temperature or settings.LLM_TEMPERATURE,
                "stream": True
            }
            
            if settings.LLM_MODEL.startswith("deepseek-v4") and thinking_enabled:
                api_params["extra_body"] = {"thinking": {"type": "enabled"}}
                api_params["reasoning_effort"] = reasoning_effort
            
            stream = self.client.chat.completions.create(**api_params)
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info("流式分析生成完成")
            
        except APIConnectionError as e:
            logger.error(f"API连接失败: {e}")
            raise AppAPIConnectionError(details=str(e))
        
        except APITimeoutError as e:
            logger.error(f"API超时: {e}")
            raise AppAPITimeoutError(timeout=settings.LLM_TIMEOUT)
        
        except RateLimitError as e:
            logger.error(f"API速率限制: {e}")
            raise AppRateLimitError(details=str(e))
        
        except APIError as e:
            logger.error(f"API错误: {e}")
            raise LLMError(
                message="API调用失败",
                details=str(e)
            )
        
        except Exception as e:
            logger.error(f"生成分析失败: {e}")
            raise LLMError(
                message="生成分析失败",
                details=str(e)
            )
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=10
            )
            logger.info("API连接测试成功")
            return True
        except Exception as e:
            logger.error(f"API连接测试失败: {e}")
            return False


# 全局LLM客户端实例
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    获取全局LLM客户端实例
    
    Returns:
        LLM客户端实例
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def generate_analysis(
    event_text: str,
    retrieved_cards: List[Dict[str, Any]],
    temperature: Optional[float] = None,
    analysis_mode: str = "minecraft",
    history_records: Optional[List[Dict[str, Any]]] = None,
    thinking_enabled: bool = True,
    reasoning_effort: str = "high"
) -> str:
    """
    生成分析报告（便捷函数）
    
    Args:
        event_text: 事件文本
        retrieved_cards: 检索到的理论卡片
        temperature: 温度参数
        analysis_mode: 分析模式 (minecraft/general)
        history_records: 检索到的历史资料
        thinking_enabled: 是否启用思考模式
        reasoning_effort: 推理努力程度
    
    Returns:
        分析报告文本
    """
    client = get_llm_client()
    return client.generate_analysis(event_text, retrieved_cards, temperature, analysis_mode, history_records, thinking_enabled, reasoning_effort)


def generate_analysis_stream(
    event_text: str,
    retrieved_cards: List[Dict[str, Any]],
    temperature: Optional[float] = None,
    analysis_mode: str = "minecraft",
    history_records: Optional[List[Dict[str, Any]]] = None,
    thinking_enabled: bool = True,
    reasoning_effort: str = "high"
) -> Generator[str, None, None]:
    """
    生成分析报告（流式输出，便捷函数）
    
    Args:
        event_text: 事件文本
        retrieved_cards: 检索到的理论卡片
        temperature: 温度参数
        analysis_mode: 分析模式 (minecraft/general)
        history_records: 检索到的历史资料
        thinking_enabled: 是否启用思考模式
        reasoning_effort: 推理努力程度
    
    Yields:
        分析报告文本片段
    """
    client = get_llm_client()
    yield from client.generate_analysis_stream(event_text, retrieved_cards, temperature, analysis_mode, history_records, thinking_enabled, reasoning_effort)
