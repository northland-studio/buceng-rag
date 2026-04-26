"""
Streamlit主界面
Minecraft游戏社科分析台 - 增强版（无emoji版）
支持知识库管理、文档导入和AI自动分析
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import time
from pathlib import Path
import json

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
import document_processor
import ai_analyzer

logger = get_logger(__name__)


# ============ 页面配置 ============

st.set_page_config(
    page_title="Minecraft游戏社科分析台",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Minecraft游戏社科分析台 - 基于RAG架构的社会学分析工具"
    }
)


# ============ 自定义CSS样式 ============

def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 主容器样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 卡片样式 */
    .card-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        margin-bottom: 10px;
    }
    
    /* 统计卡片 */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    /* 按钮样式 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* 文本输入框 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    /* 侧边栏样式 */
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 文件上传区域 */
    .uploadedFile {
        border-radius: 8px;
    }
    
    /* 引用高亮 */
    .reference-highlight {
        background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* 分析结果卡片 */
    .analysis-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    
    /* 加载动画 */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)


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
    if 'page' not in st.session_state:
        st.session_state.page = '主页'
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    
    if 'current_cards' not in st.session_state:
        st.session_state.current_cards = []
    
    if 'streaming_enabled' not in st.session_state:
        st.session_state.streaming_enabled = True
    
    if 'editing_card' not in st.session_state:
        st.session_state.editing_card = None


# ============ 错误处理 ============

def show_error(message: str, details: Optional[str] = None):
    """显示错误消息"""
    st.error(f"错误: {message}")
    if details:
        with st.expander("查看详细错误信息"):
            st.code(details)
    logger.error(f"{message} - {details}" if details else message)


def show_success(message: str):
    """显示成功消息"""
    st.success(f"成功: {message}")
    logger.info(message)


def show_warning(message: str):
    """显示警告消息"""
    st.warning(f"警告: {message}")
    logger.warning(message)


def show_info(message: str):
    """显示信息消息"""
    st.info(f"提示: {message}")


# ============ 侧边栏 ============

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # 标题
        st.title("Minecraft游戏社科分析台")
        st.caption("基于RAG架构的社会学分析工具")
        
        st.divider()
        
        # 页面导航
        st.subheader("导航")
        page = st.radio(
            "选择页面",
            ["主页", "知识库管理", "文档导入分析", "系统设置"],
            key="page_selector",
            label_visibility="collapsed"
        )
        st.session_state.page = page
        
        st.divider()
        
        # 知识库统计
        render_knowledge_stats()
        
        st.divider()
        
        # 快速操作
        st.subheader("快速操作")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("添加卡片", use_container_width=True):
                st.session_state.page = "知识库管理"
                st.rerun()
        
        with col2:
            if st.button("导入文档", use_container_width=True):
                st.session_state.page = "文档导入分析"
                st.rerun()
        
        st.divider()
        
        # 系统信息
        st.caption(f"版本: v1.2.0")
        st.caption(f"模型: {settings.EMBEDDING_MODEL_NAME}")


def render_knowledge_stats():
    """渲染知识库统计信息"""
    st.subheader("知识库统计")
    
    try:
        kb = get_knowledge_base_instance()
        stats = kb.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "理论卡片",
                stats.get('total_cards', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "黄金样本",
                stats.get('golden_samples', 0),
                delta=None
            )
        
        # 进度条
        if stats.get('total_cards', 0) > 0:
            st.progress(min(stats.get('total_cards', 0) / 100, 1.0))
        
    except Exception as e:
        show_error("获取知识库统计失败", str(e))


# ============ 主页 ============

def render_home_page():
    """渲染主页"""
    st.title("主页")
    st.markdown("---")
    
    # 欢迎信息
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 欢迎使用Minecraft游戏社科分析台
        
        本系统基于RAG（检索增强生成）架构，帮助您分析Minecraft游戏内的社会学现象。
        
        **主要功能：**
        - 智能理论检索
        - AI分析生成
        - 知识库管理
        - 文档导入分析
        """)
    
    st.markdown("---")
    
    # 事件输入区
    render_event_input()
    
    # 分析结果区
    if st.session_state.current_analysis:
        render_analysis_result()


def render_event_input():
    """渲染事件输入区"""
    st.subheader("游戏事件描述")
    
    # 事件文本输入
    event_text = st.text_area(
        "请输入游戏内结构化的事件文本",
        placeholder="例如：玩家在公共农场收割后不补种，导致冲突并催生规则",
        height=150,
        help="描述游戏内的社会现象或事件，系统将自动检索相关理论并生成分析",
        key="event_input"
    )
    
    # 配置选项
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
    
    with col1:
        st.session_state.streaming_enabled = st.checkbox(
            "启用流式输出",
            value=st.session_state.streaming_enabled,
            help="实时显示分析结果"
        )
    
    with col2:
        k = st.number_input(
            "检索数量",
            min_value=1,
            max_value=10,
            value=settings.MAX_RETRIEVAL_RESULTS,
            help="检索的理论卡片数量"
        )
    
    with col3:
        temperature = st.slider(
            "创造性",
            min_value=0.0,
            max_value=1.0,
            value=settings.LLM_TEMPERATURE,
            step=0.1,
            help="LLM温度参数，越高越有创造性"
        )
    
    with col4:
        st.write("")  # 占位
        st.write("")
    
    # 提交按钮
    analyze_button = st.button(
        "提交分析",
        type="primary",
        use_container_width=True
    )
    
    if analyze_button and event_text:
        perform_analysis(event_text, k, temperature)


def perform_analysis(event_text: str, k: int, temperature: float):
    """执行分析"""
    try:
        # 验证输入
        event_text = utils.validate_input(event_text)
        
        # 清洗文本
        event_text = utils.clean_event_text(event_text)
        
        # 显示进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("正在检索相关理论...")
        progress_bar.progress(30)
        
        # 检索理论卡片
        kb = get_knowledge_base_instance()
        cards = kb.search_similar(event_text, k=k)
        
        if not cards:
            show_warning("未找到相关理论卡片，分析可能不够准确")
        
        progress_bar.progress(50)
        
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
        
        status_text.text("正在生成分析...")
        progress_bar.progress(70)
        
        # 生成分析
        if st.session_state.streaming_enabled:
            # 流式输出
            analysis_placeholder = st.empty()
            analysis_text = ""
            
            client = get_llm_client_instance()
            for chunk in client.generate_analysis_stream(event_text, cards, temperature):
                analysis_text += chunk
                analysis_placeholder.markdown(analysis_text)
            
            st.session_state.current_analysis = analysis_text
            
        else:
            # 非流式输出
            analysis = llm_api.generate_analysis(event_text, cards, temperature)
            st.session_state.current_analysis = analysis
        
        progress_bar.progress(100)
        status_text.text("分析完成！")
        
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
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
    st.markdown("---")
    st.subheader("分析结果")
    
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
            with st.expander(f"**{card['title']}** [{ref_id}]", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**内容**: {card['content']}")
                with col2:
                    st.metric("相似度", f"{card.get('similarity', 0):.2%}")
                
                st.markdown(f"**来源**: {card['source']}")
                if card['keywords']:
                    st.markdown(f"**关键词**: {', '.join(card['keywords'])}")
        else:
            st.warning(f"未找到引用的理论卡片: {ref_id}")


def render_rating_section(event_text: str):
    """渲染评分和保存区"""
    st.markdown("---")
    st.subheader("评价与保存")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        rating = st.radio(
            "分析质量评分",
            options=[1, 2, 3],
            format_func=lambda x: ["差", "中", "好"][x-1],
            horizontal=True
        )
    
    with col2:
        st.write("")
    
    with col3:
        if st.button("保存为黄金样本", type="primary", use_container_width=True):
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


# ============ 知识库管理页面 ============

def render_knowledge_base_page():
    """渲染知识库管理页面"""
    st.title("知识库管理")
    st.markdown("---")
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["卡片列表", "添加卡片", "批量导入"])
    
    with tab1:
        render_card_list()
    
    with tab2:
        render_add_card_form()
    
    with tab3:
        render_batch_import()


def render_card_list():
    """渲染卡片列表"""
    st.subheader("理论卡片列表")
    
    # 搜索和筛选
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "搜索卡片",
            placeholder="输入关键词搜索...",
            key="card_search"
        )
    
    with col2:
        sort_by = st.selectbox(
            "排序方式",
            ["标题", "创建时间", "更新时间"],
            key="card_sort"
        )
    
    with col3:
        view_mode = st.radio(
            "视图模式",
            ["卡片", "表格"],
            horizontal=True,
            key="card_view"
        )
    
    # 获取卡片列表
    try:
        kb = get_knowledge_base_instance()
        
        # 如果有搜索查询，使用搜索功能
        if search_query:
            cards = kb.search_similar(search_query, k=50)
        else:
            # 否则获取所有卡片（需要实现）
            cards = []
            show_info("请使用搜索功能查找卡片")
        
        if cards:
            if view_mode == "卡片":
                # 卡片视图
                for i in range(0, len(cards), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(cards):
                            with cols[j]:
                                render_card_item(cards[i + j])
            else:
                # 表格视图
                render_card_table(cards)
        else:
            if not search_query:
                show_info("知识库中暂无卡片，请添加或导入")
    
    except Exception as e:
        show_error("获取卡片列表失败", str(e))


def render_card_item(card: Dict[str, Any]):
    """渲染单个卡片项"""
    with st.container():
        st.markdown(f"""
        <div style='background: white; border-radius: 10px; padding: 15px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px;
                    border-left: 4px solid #667eea;'>
            <h4>{card['title']}</h4>
            <p style='color: #666;'>{card['content'][:100]}...</p>
            <small>来源: {card['source']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("编辑", key=f"edit_{card['id']}", use_container_width=True):
                st.session_state.editing_card = card['id']
        
        with col2:
            if st.button("删除", key=f"delete_{card['id']}", use_container_width=True):
                if kb.delete_card(card['id']):
                    show_success("卡片删除成功")
                    st.rerun()
                else:
                    show_error("卡片删除失败")


def render_card_table(cards: List[Dict[str, Any]]):
    """渲染卡片表格"""
    import pandas as pd
    
    df_data = []
    for card in cards:
        df_data.append({
            "ID": card['id'],
            "标题": card['title'],
            "内容": card['content'][:50] + "...",
            "来源": card['source'],
            "相似度": f"{card.get('similarity', 0):.2%}"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)


def render_add_card_form():
    """渲染添加卡片表单"""
    st.subheader("添加新卡片")
    
    with st.form("add_card_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            card_id = st.text_input(
                "卡片ID *",
                placeholder="例如: theory_001",
                help="唯一标识符，建议使用英文和下划线"
            )
            
            title = st.text_input(
                "标题 *",
                placeholder="理论标题"
            )
            
            keywords = st.text_input(
                "关键词",
                placeholder="用逗号分隔，例如: 公共资源,治理",
                help="用于检索和分类"
            )
        
        with col2:
            content = st.text_area(
                "内容 *",
                placeholder="理论内容描述",
                height=150
            )
            
            source = st.text_input(
                "来源",
                placeholder="例如: 作者 (年份). 论文标题"
            )
        
        submitted = st.form_submit_button("添加卡片", type="primary", use_container_width=True)
        
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
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        show_warning("卡片可能已存在或添加失败")
                        
                except Exception as e:
                    show_error("添加卡片失败", str(e))


def render_batch_import():
    """渲染批量导入功能"""
    st.subheader("批量导入卡片")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "上传JSON文件",
        type=['json'],
        help="文件格式: [{id, title, content, keywords, source}, ...]"
    )
    
    if uploaded_file is not None:
        try:
            # 读取文件内容
            content = uploaded_file.read().decode('utf-8')
            cards = json.loads(content)
            
            if not isinstance(cards, list):
                show_error("文件格式错误：应为JSON数组")
            else:
                st.info(f"检测到 {len(cards)} 张卡片")
                
                # 预览前5张卡片
                with st.expander("预览卡片", expanded=False):
                    for i, card in enumerate(cards[:5], 1):
                        st.markdown(f"**{i}. {card.get('title', 'N/A')}**")
                        st.caption(f"ID: {card.get('id', 'N/A')}")
                        st.caption(card.get('content', 'N/A')[:100] + "...")
                        st.divider()
                
                if st.button("确认导入", type="primary", use_container_width=True):
                    try:
                        kb = get_knowledge_base_instance()
                        count = kb.add_cards(cards)
                        show_success(f"成功导入 {count} 张卡片")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        show_error("导入失败", str(e))
                        
        except json.JSONDecodeError:
            show_error("JSON文件解析失败")
        except Exception as e:
            show_error("文件读取失败", str(e))
    
    # 模板下载
    st.markdown("---")
    st.subheader("下载模板")
    
    template = [
        {
            "id": "example_001",
            "title": "示例理论",
            "content": "这是一个示例理论卡片的内容描述。",
            "keywords": ["示例", "模板"],
            "source": "示例来源"
        }
    ]
    
    st.download_button(
        label="下载JSON模板",
        data=json.dumps(template, ensure_ascii=False, indent=2),
        file_name="card_template.json",
        mime="application/json",
        use_container_width=True
    )


# ============ 文档导入分析页面 ============

def render_document_import_page():
    """渲染文档导入分析页面"""
    st.title("文档导入分析")
    st.markdown("---")
    
    # 标签页
    tab1, tab2 = st.tabs(["上传文档", "文档列表"])
    
    with tab1:
        render_document_upload()
    
    with tab2:
        render_document_list()


def render_document_upload():
    """渲染文档上传"""
    st.subheader("上传文档")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "上传文档文件",
        type=['txt', 'md', 'json', 'pdf', 'docx'],
        accept_multiple_files=True,
        help="支持格式: TXT, Markdown, JSON, PDF, DOCX"
    )
    
    if uploaded_files:
        st.info(f"已选择 {len(uploaded_files)} 个文件")
        
        # 显示文件列表
        for file in uploaded_files:
            with st.expander(f"{file.name}", expanded=False):
                # 读取文件内容
                try:
                    # 根据文件类型处理
                    if file.name.endswith('.pdf'):
                        text = document_processor.extract_text_from_uploaded_file(file)
                    elif file.name.endswith('.docx'):
                        text = document_processor.extract_text_from_uploaded_file(file)
                    else:
                        content = file.read().decode('utf-8')
                        file.seek(0)
                        text = content
                    
                    # 显示文件信息
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.metric("文件大小", f"{len(text)} 字符")
                    with col2:
                        st.metric("行数", len(text.split('\n')))
                    
                    # 显示内容预览
                    st.text_area(
                        "内容预览",
                        value=text[:500] + "..." if len(text) > 500 else text,
                        height=200,
                        disabled=True
                    )
                except Exception as e:
                    show_error(f"文件读取失败: {file.name}", str(e))
        
        # 分析选项
        st.markdown("---")
        st.subheader("分析选项")
        
        col1, col2 = st.columns(2)
        with col1:
            analysis_mode = st.radio(
                "分析模式",
                ["AI自动分析", "简单分割", "手动处理"],
                help="AI自动分析：使用AI分析内容并生成知识卡片\n简单分割：按段落分割文本\n手动处理：仅上传不处理"
            )
        
        with col2:
            auto_import = st.checkbox(
                "自动导入到知识库",
                value=True,
                help="将处理结果自动导入到知识库"
            )
        
        # 高级选项
        with st.expander("高级选项", expanded=False):
            chunk_size = st.slider(
                "文本块大小",
                min_value=200,
                max_value=2000,
                value=500,
                step=100,
                help="文本分割的块大小"
            )
            
            enable_ai_analysis = st.checkbox(
                "启用AI深度分析",
                value=True,
                help="使用AI分析每个文本块并提取关键信息"
            )
        
        # 开始分析按钮
        if st.button("开始处理", type="primary", use_container_width=True):
            perform_document_analysis(uploaded_files, analysis_mode, auto_import, chunk_size, enable_ai_analysis)


def perform_document_analysis(
    files: List,
    mode: str,
    auto_import: bool,
    chunk_size: int,
    enable_ai_analysis: bool
):
    """执行文档分析"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        kb = get_knowledge_base_instance()
        all_cards = []
        
        for i, file in enumerate(files):
            status_text.text(f"正在处理: {file.name} ({i+1}/{len(files)})")
            progress_bar.progress((i + 1) / len(files) * 100)
            
            try:
                # 提取文本
                if file.name.endswith('.pdf') or file.name.endswith('.docx'):
                    text = document_processor.extract_text_from_uploaded_file(file)
                else:
                    text = file.read().decode('utf-8')
                    file.seek(0)
                
                # 根据模式处理
                if mode == "AI自动分析" and enable_ai_analysis:
                    # 使用AI分析
                    status_text.text(f"AI分析中: {file.name}")
                    cards = ai_analyzer.analyze_document_with_ai(text, file.name)
                    
                elif mode == "简单分割":
                    # 简单分割
                    cards = document_processor.process_document_for_knowledge_base(
                        text, file.name, chunk_size
                    )
                    
                else:
                    # 手动处理，不生成卡片
                    cards = []
                    show_info(f"文件 {file.name} 已上传，请手动处理")
                
                all_cards.extend(cards)
                
            except Exception as e:
                show_error(f"处理文件 {file.name} 失败", str(e))
                continue
        
        # 自动导入
        if auto_import and all_cards:
            status_text.text("正在导入到知识库...")
            count = kb.add_cards(all_cards)
            show_success(f"成功处理 {len(files)} 个文档，导入 {count} 张卡片")
        else:
            show_success(f"成功处理 {len(files)} 个文档，生成 {len(all_cards)} 张卡片")
        
        progress_bar.empty()
        status_text.empty()
        
        # 显示生成的卡片
        if all_cards and not auto_import:
            with st.expander("查看生成的卡片", expanded=False):
                for i, card in enumerate(all_cards[:10], 1):
                    st.markdown(f"**{i}. {card.get('title', 'N/A')}**")
                    st.caption(card.get('content', 'N/A')[:200] + "...")
                    st.divider()
                
                if len(all_cards) > 10:
                    st.info(f"还有 {len(all_cards) - 10} 张卡片未显示")
                
                # 手动导入按钮
                if st.button("导入所有卡片", type="primary"):
                    count = kb.add_cards(all_cards)
                    show_success(f"成功导入 {count} 张卡片")
                    st.rerun()
    
    except Exception as e:
        show_error("文档分析失败", str(e))
        logger.exception("文档分析失败")


def render_document_list():
    """渲染文档列表"""
    st.subheader("已上传文档")
    
    # 这里应该显示已上传的文档列表
    # 由于Streamlit的限制，需要实现持久化存储
    show_info("文档列表功能开发中...")


# ============ 系统设置页面 ============

def render_settings_page():
    """渲染系统设置页面"""
    st.title("系统设置")
    st.markdown("---")
    
    # 系统信息
    st.subheader("系统信息")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Python版本", "3.11.9")
        st.metric("嵌入模型", settings.EMBEDDING_MODEL_NAME)
    
    with col2:
        st.metric("LLM模型", settings.LLM_MODEL)
        st.metric("向量维度", "1024")
    
    # 配置信息
    st.markdown("---")
    st.subheader("当前配置")
    
    config_data = {
        "DeepSeek API": {
            "Base URL": settings.DEEPSEEK_BASE_URL,
            "Model": settings.LLM_MODEL,
            "Temperature": settings.LLM_TEMPERATURE,
            "Timeout": f"{settings.LLM_TIMEOUT}s"
        },
        "嵌入模型": {
            "Model": settings.EMBEDDING_MODEL_NAME,
            "Device": settings.EMBEDDING_DEVICE,
            "HF Endpoint": settings.HF_ENDPOINT or "默认"
        },
        "知识库": {
            "Persist Dir": settings.CHROMA_PERSIST_DIR,
            "Collection": settings.COLLECTION_NAME
        },
        "应用": {
            "Max Input Length": settings.MAX_INPUT_LENGTH,
            "Max Retrieval Results": settings.MAX_RETRIEVAL_RESULTS,
            "Log Level": settings.LOG_LEVEL
        }
    }
    
    for section, configs in config_data.items():
        st.markdown(f"**{section}**")
        for key, value in configs.items():
            st.text(f"{key}: {value}")
        st.markdown("")
    
    # 数据管理
    st.markdown("---")
    st.subheader("数据管理")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("导出黄金样本", use_container_width=True):
            try:
                kb = get_knowledge_base_instance()
                count = kb.export_golden_samples(settings.GOLDEN_SAMPLES_FILE)
                if count > 0:
                    show_success(f"成功导出 {count} 个黄金样本")
                else:
                    show_info("没有黄金样本可导出")
            except Exception as e:
                show_error("导出失败", str(e))
    
    with col2:
        if st.button("清空知识库", use_container_width=True):
            if st.checkbox("确认清空"):
                show_warning("此操作不可恢复！")
    
    with col3:
        if st.button("重置系统", use_container_width=True):
            show_warning("此操作将重置所有设置")


# ============ 主函数 ============

def main():
    """主函数"""
    try:
        # 加载自定义CSS
        load_custom_css()
        
        # 初始化会话状态
        init_session_state()
        
        # 初始化知识库和LLM客户端
        get_knowledge_base_instance()
        get_llm_client_instance()
        
        # 渲染侧边栏
        render_sidebar()
        
        # 根据页面选择渲染内容
        if st.session_state.page == "主页":
            render_home_page()
        elif st.session_state.page == "知识库管理":
            render_knowledge_base_page()
        elif st.session_state.page == "文档导入分析":
            render_document_import_page()
        elif st.session_state.page == "系统设置":
            render_settings_page()
        
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        st.info("请检查配置文件和日志")
        logger.exception("系统初始化失败")


if __name__ == "__main__":
    main()
