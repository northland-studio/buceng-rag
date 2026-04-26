"""
Streamlit主界面
Minecraft游戏社科分析台
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import time
from pathlib import Path

from logger import get_logger, setup_logger
from config import settings
from exceptions import (
    BaseAppException,
    InvalidInputError,
    LLMError,
    KnowledgeBaseError
)
import knowledge_base
import llm_api
import utils

logger = get_logger(__name__)


# ============ 页面配置 ============

st.set_page_config(
    page_title="Minecraft游戏社科分析台",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============ 缓存资源 ============

@st.cache_resource
def get_knowledge_base_instance():
    """获取知识库实例（缓存）"""
    return knowledge_base.get_knowledge_base()


@st.cache_resource
def get_llm_client_instance():
    """获取LLM客户端实例（缓存）"""
    return llm_api.get_llm_client()


# ============ 会话状态初始化 ============

def init_session_state():
    """初始化会话状态"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    
    if 'current_cards' not in st.session_state:
        st.session_state.current_cards = []
    
    if 'streaming_enabled' not in st.session_state:
        st.session_state.streaming_enabled = True


# ============ 错误处理 ============

def show_error(message: str, details: Optional[str] = None):
    """显示错误消息"""
    st.error(f"错误: {message}")
    if details:
        st.caption(details)
    logger.error(f"{message} - {details}" if details else message)


def show_success(message: str):
    """显示成功消息"""
    st.success(message)
    logger.info(message)


def show_warning(message: str):
    """显示警告消息"""
    st.warning(message)
    logger.warning(message)


# ============ 侧边栏 ============

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("控制面板")
        
        # 知识库统计
        render_knowledge_stats()
        
        st.divider()
        
        # 添加理论卡片
        render_add_card_form()
        
        st.divider()
        
        # 批量导入
        render_batch_import()
        
        st.divider()
        
        # 检索测试
        render_search_test()


def render_knowledge_stats():
    """渲染知识库统计信息"""
    st.subheader("知识库统计")
    
    try:
        kb = get_knowledge_base_instance()
        stats = kb.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("理论卡片", stats.get('total_cards', 0))
        with col2:
            st.metric("黄金样本", stats.get('golden_samples', 0))
        
        st.caption(f"集合: {stats.get('collection_name', 'N/A')}")
        
    except Exception as e:
        show_error("获取知识库统计失败", str(e))


def render_add_card_form():
    """渲染添加理论卡片表单"""
    st.subheader("添加理论卡片")
    
    with st.form("add_card_form"):
        card_id = st.text_input("卡片ID *", placeholder="例如: theory_001")
        title = st.text_input("标题 *", placeholder="理论标题")
        content = st.text_area("内容 *", placeholder="理论内容描述", height=100)
        keywords = st.text_input("关键词", placeholder="用逗号分隔，例如: 公共资源,治理")
        source = st.text_input("来源", placeholder="例如: 作者 (年份). 论文标题")
        
        submitted = st.form_submit_button("添加卡片", type="primary")
        
        if submitted:
            # 验证必填字段
            if not all([card_id, title, content]):
                show_error("请填写所有必填字段")
            else:
                try:
                    card = {
                        'id': card_id.strip(),
                        'title': title.strip(),
                        'content': content.strip(),
                        'keywords': [k.strip() for k in keywords.split(',') if k.strip()],
                        'source': source.strip()
                    }
                    
                    kb = get_knowledge_base_instance()
                    count = kb.add_cards([card])
                    
                    if count > 0:
                        show_success(f"成功添加卡片: {card_id}")
                        st.rerun()
                    else:
                        show_warning("卡片可能已存在或添加失败")
                        
                except Exception as e:
                    show_error("添加卡片失败", str(e))


def render_batch_import():
    """渲染批量导入功能"""
    st.subheader("批量导入卡片")
    
    uploaded_file = st.file_uploader(
        "上传JSON文件",
        type=['json'],
        help="文件格式: [{id, title, content, keywords, source}, ...]"
    )
    
    if uploaded_file is not None:
        try:
            import json
            cards = json.load(uploaded_file)
            
            if not isinstance(cards, list):
                show_error("文件格式错误：应为JSON数组")
            else:
                st.info(f"检测到 {len(cards)} 张卡片")
                
                if st.button("确认导入", type="primary"):
                    kb = get_knowledge_base_instance()
                    count = kb.add_cards(cards)
                    show_success(f"成功导入 {count} 张卡片")
                    st.rerun()
                    
        except json.JSONDecodeError:
            show_error("JSON文件解析失败")
        except Exception as e:
            show_error("导入失败", str(e))


def render_search_test():
    """渲染检索测试功能"""
    st.subheader("检索测试")
    
    query = st.text_input("查询文本", placeholder="输入查询内容")
    k = st.slider("返回数量", 1, 10, 5)
    
    if st.button("检索", type="primary") and query:
        try:
            kb = get_knowledge_base_instance()
            results = kb.search_similar(query, k=k)
            
            if results:
                st.success(f"找到 {len(results)} 个相关结果")
                
                for i, card in enumerate(results, 1):
                    with st.expander(
                        f"{i}. {card['title']} (相似度: {card['similarity']:.2%})",
                        expanded=(i == 1)
                    ):
                        st.markdown(f"**ID**: {card['id']}")
                        st.markdown(f"**内容**: {card['content']}")
                        st.markdown(f"**来源**: {card['source']}")
                        if card['keywords']:
                            st.markdown(f"**关键词**: {', '.join(card['keywords'])}")
            else:
                st.info("未找到相关结果")
                
        except Exception as e:
            show_error("检索失败", str(e))


# ============ 主页内容 ============

def render_main_page():
    """渲染主页内容"""
    st.title("Minecraft游戏社科分析台")
    st.markdown("---")
    
    # 事件输入区
    render_event_input()
    
    # 分析结果区
    render_analysis_result()


def render_event_input():
    """渲染事件输入区"""
    st.subheader("游戏事件描述")
    
    # 事件文本输入
    event_text = st.text_area(
        "请输入游戏内结构化的事件文本",
        placeholder="例如：玩家在公共农场收割后不补种，导致冲突并催生规则",
        height=150,
        help="描述游戏内的社会现象或事件，系统将自动检索相关理论并生成分析"
    )
    
    # 配置选项
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.session_state.streaming_enabled = st.checkbox(
            "启用流式输出",
            value=st.session_state.streaming_enabled
        )
    
    with col2:
        k = st.number_input(
            "检索数量",
            min_value=1,
            max_value=10,
            value=settings.MAX_RETRIEVAL_RESULTS
        )
    
    with col3:
        temperature = st.slider(
            "创造性",
            min_value=0.0,
            max_value=1.0,
            value=settings.LLM_TEMPERATURE,
            step=0.1
        )
    
    # 提交按钮
    analyze_button = st.button("提交分析", type="primary", use_container_width=True)
    
    if analyze_button and event_text:
        perform_analysis(event_text, k, temperature)


def perform_analysis(event_text: str, k: int, temperature: float):
    """
    执行分析
    
    Args:
        event_text: 事件文本
        k: 检索数量
        temperature: 温度参数
    """
    try:
        # 验证输入
        event_text = utils.validate_input(event_text)
        
        # 清洗文本
        event_text = utils.clean_event_text(event_text)
        
        # 显示进度
        with st.spinner("正在检索相关理论..."):
            kb = get_knowledge_base_instance()
            cards = kb.search_similar(event_text, k=k)
        
        if not cards:
            show_warning("未找到相关理论卡片，分析可能不够准确")
        
        # 保存检索结果
        st.session_state.current_cards = cards
        
        # 显示检索到的卡片
        if cards:
            with st.expander(f"检索到 {len(cards)} 个相关理论", expanded=False):
                for i, card in enumerate(cards, 1):
                    st.markdown(f"**{i}. {card['title']}** (相似度: {card['similarity']:.2%})")
                    st.caption(card['content'])
                    st.caption(f"来源: {card['source']}")
                    st.divider()
        
        # 生成分析
        st.subheader("分析结果")
        
        if st.session_state.streaming_enabled:
            # 流式输出
            analysis_placeholder = st.empty()
            analysis_text = ""
            
            with st.spinner("正在生成分析..."):
                client = get_llm_client_instance()
                for chunk in client.generate_analysis_stream(event_text, cards, temperature):
                    analysis_text += chunk
                    analysis_placeholder.markdown(analysis_text)
            
            st.session_state.current_analysis = analysis_text
            
        else:
            # 非流式输出
            with st.spinner("正在生成分析..."):
                analysis = llm_api.generate_analysis(event_text, cards, temperature)
                st.markdown(analysis)
                st.session_state.current_analysis = analysis
        
        # 显示引用的理论卡片
        render_referenced_cards()
        
        # 评分和保存
        render_rating_section(event_text)
        
    except InvalidInputError as e:
        show_error("输入验证失败", str(e))
    except LLMError as e:
        show_error("分析生成失败", str(e))
    except Exception as e:
        show_error("系统错误", str(e))
        logger.exception("分析过程发生未知错误")


def render_analysis_result():
    """渲染分析结果区"""
    if st.session_state.current_analysis:
        st.markdown("---")
        st.subheader("历史分析")
        
        # 显示当前分析
        st.markdown(st.session_state.current_analysis)
        
        # 显示引用的理论卡片
        render_referenced_cards()
        
        # 评分和保存
        if st.session_state.get('last_event'):
            render_rating_section(st.session_state.last_event)


def render_referenced_cards():
    """渲染引用的理论卡片"""
    if not st.session_state.current_analysis:
        return
    
    # 解析引用
    references = utils.parse_references(st.session_state.current_analysis)
    
    if not references:
        return
    
    st.markdown("---")
    st.subheader("引用的理论卡片")
    
    kb = get_knowledge_base_instance()
    
    for ref_id in references:
        card = kb.get_card(ref_id)
        
        if card:
            with st.expander(f"{card['title']} [{ref_id}]", expanded=False):
                st.markdown(f"**内容**: {card['content']}")
                st.markdown(f"**来源**: {card['source']}")
                if card['keywords']:
                    st.markdown(f"**关键词**: {', '.join(card['keywords'])}")
        else:
            st.warning(f"未找到引用的理论卡片: {ref_id}")


def render_rating_section(event_text: str):
    """渲染评分和保存区"""
    st.markdown("---")
    st.subheader("评价与保存")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        rating = st.radio(
            "分析质量评分",
            options=[1, 2, 3],
            format_func=lambda x: ["差", "中", "好"][x-1] + f" ({x}星)",
            horizontal=True
        )
    
    with col2:
        if st.button("保存为黄金样本", type="primary"):
            try:
                # 保存到知识库
                kb = get_knowledge_base_instance()
                card_ids = [card['id'] for card in st.session_state.current_cards]
                
                success = kb.add_golden_sample(
                    event=event_text,
                    analysis=st.session_state.current_analysis,
                    rating=rating,
                    retrieved_cards=card_ids
                )
                
                # 同时保存到文件
                utils.save_golden_sample(
                    event=event_text,
                    analysis=st.session_state.current_analysis,
                    rating=rating,
                    retrieved_cards=card_ids
                )
                
                if success:
                    show_success("黄金样本保存成功")
                else:
                    show_warning("黄金样本保存到知识库失败，但已保存到文件")
                    
            except Exception as e:
                show_error("保存失败", str(e))


# ============ 主函数 ============

def main():
    """主函数"""
    try:
        # 初始化会话状态
        init_session_state()
        
        # 初始化知识库和LLM客户端
        get_knowledge_base_instance()
        get_llm_client_instance()
        
        # 渲染侧边栏
        render_sidebar()
        
        # 渲染主页
        render_main_page()
        
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        st.info("请检查配置文件和日志")
        logger.exception("系统初始化失败")


if __name__ == "__main__":
    main()
