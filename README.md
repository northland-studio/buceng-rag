# 不曾社科理论RAG分析系统

<div align="center">

<img src="logo.png" alt="BucengRAG Logo" width="180">

**Buceng Social Science RAG Analysis System**

基于检索增强生成架构的社会科学理论分析平台

---

![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Status](https://img.shields.io/badge/status-active%20development-brightgreen.svg)

![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-orange)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-blue)
![BGE](https://img.shields.io/badge/BGE--large--zh-v1.5-green)

---

**开发者**: 北域工作室 (Northland Comprehensive Studio)

**官网**: [https://beiyu.xuanjian.top](https://beiyu.xuanjian.top/)

</div>

---

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [知识库内容](#知识库内容)
- [配置说明](#配置说明)
- [开发计划](#开发计划)
- [开发者信息](#开发者信息)

---

## 项目简介

不曾社科理论RAG分析系统是一个专业的社会科学理论分析平台，采用检索增强生成(RAG)架构，整合了马克思主义理论、社会学、政治学、经济学等多学科知识体系。系统能够对游戏内社会现象和现实社会现象进行深入的理论分析，为用户提供专业的社会科学视角。

### 设计理念

- **理论驱动**: 以经典社会科学理论为核心，确保分析的专业性和深度
- **历史参照**: 整合人类文明历史资料，提供历史背景和相似事件参考
- **智能检索**: 基于向量相似度的语义检索，精准匹配相关理论
- **开放架构**: 模块化设计，支持自定义扩展和多模型切换

---

## 核心特性

### 双模式分析

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| Minecraft游戏分析 | 针对游戏内社会现象的理论分析 | 游戏社区研究、虚拟社会分析 |
| 普通社科分析 | 针对现实社会现象的理论分析 | 社会问题研究、现象解读 |

### 智能知识检索

- 基于向量语义相似度的理论卡片检索
- 历史资料库联动检索，提供历史参照
- 可调节检索数量和相关性阈值

### 多格式文档导出

- Markdown格式：适合技术文档和在线发布
- Word文档：适合学术报告和正式文档
- 自动标注理论引用和生成信息

### 知识库管理

- 理论卡片管理：添加、编辑、删除、批量导入
- 历史资料管理：时期分类、关键词检索
- 黄金样本：高质量分析样本的保存与复用

---

## 系统架构

```
                                    +------------------+
                                    |   Streamlit UI   |
                                    +--------+---------+
                                             |
                    +------------------------+------------------------+
                    |                        |                        |
           +--------v--------+       +-------v-------+       +-------v-------+
           |  事件输入模块   |       |  知识库管理   |       |  文档处理     |
           +--------+--------+       +-------+-------+       +-------+-------+
                    |                        |                        |
                    |                        |                        |
           +--------v--------+       +-------v-------+       +-------v-------+
           |   分析模式选择   |       |   ChromaDB    |       |  PDF/DOCX    |
           +--------+--------+       +-------+-------+       +-------+-------+
                    |                        |                        |
                    +------------+-----------+-----------+------------+
                                 |                       |
                        +--------v--------+       +------v------+
                        |  向量嵌入模型   |       |  LLM API    |
                        | (BGE-large-zh) |       | (DeepSeek)  |
                        +--------+--------+       +------+------+
                                 |                       |
                        +--------v--------+       +------v------+
                        |   理论卡片检索   |       |  分析生成   |
                        +--------+--------+       +------+------+
                                 |                       |
                        +--------v--------+       +------v------+
                        |   历史资料检索   |------>|  结果输出   |
                        +-----------------+       +-------------+
```

### 目录结构

```
BUCENG/
|-- app.py                          # Streamlit主应用入口
|-- config.py                       # 配置管理模块
|-- knowledge_base.py               # 知识库核心模块
|-- llm_api.py                      # LLM API封装
|-- embedding.py                    # 向量嵌入模块
|-- document_processor.py           # 文档解析处理
|-- document_exporter.py            # 文档导出工具
|-- ai_analyzer.py                  # AI自动分析器
|-- utils.py                        # 通用工具函数
|-- logger.py                       # 日志管理
|-- exceptions.py                   # 异常定义
|--
|-- chroma_db/                      # ChromaDB向量数据库
|   |-- sociology_cards/            # 理论卡片集合
|   |-- golden_samples/             # 黄金样本集合
|   |-- history_records/            # 历史资料集合
|--
|-- data/                           # 数据文件目录
|   |-- social_theory_cards.json           # 基础社科理论 (20张)
|   |-- marxism_leninism_mao_cards.json    # 马列毛理论 (48张)
|   |-- general_social_theory_cards.json   # 通用社科理论 (90张)
|   |-- human_civilization_history.json    # 人类文明历史 (39条)
|--
|-- golden_samples/                 # 黄金样本存储目录
|-- logs/                           # 日志文件目录
|-- logo.png                        # 产品标识
|-- README.md                       # 项目说明
|-- report.md                       # 项目报告
|-- plan.md                         # 开发计划
|-- requirements.txt                # Python依赖
|-- .env                            # 环境变量配置
```

---

## 技术栈

<table>
<tr>
<td width="200"><strong>类别</strong></td>
<td><strong>技术选型</strong></td>
</tr>
<tr>
<td>前端框架</td>
<td>Streamlit 1.28+</td>
</tr>
<tr>
<td>向量数据库</td>
<td>ChromaDB 0.4+</td>
</tr>
<tr>
<td>嵌入模型</td>
<td>BAAI/bge-large-zh-v1.5 (本地部署)</td>
</tr>
<tr>
<td>LLM服务</td>
<td>DeepSeek API</td>
</tr>
<tr>
<td>文档处理</td>
<td>pdfplumber, python-docx</td>
</tr>
<tr>
<td>配置管理</td>
<td>pydantic-settings</td>
</tr>
<tr>
<td>日志系统</td>
<td>loguru</td>
</tr>
</table>

---

## 快速开始

### 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.10 或更高版本 |
| 内存 | 8GB 以上 (推荐16GB) |
| 存储 | 5GB 以上可用空间 |
| 网络 | 需要网络连接 (API调用) |

### 安装步骤

**1. 克隆项目**

```bash
git clone https://github.com/your-repo/BUCENG.git
cd BUCENG
```

**2. 创建虚拟环境**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

**4. 配置环境变量**

创建 `.env` 文件并填入配置：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 模型配置
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7

# HuggingFace镜像 (国内用户推荐)
HF_ENDPOINT=https://hf-mirror.com
```

**5. 启动应用**

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

---

## 使用指南

### 理论分析流程

```
输入事件/现象描述
        |
        v
选择分析模式 (Minecraft/普通社科)
        |
        v
设置检索参数 (数量、创造性)
        |
        v
提交分析 --> 理论卡片检索 --> 历史资料检索
        |                           |
        v                           v
    LLM分析生成 <---- 整合检索结果
        |
        v
查看分析结果 --> 导出报告 (MD/DOCX)
        |
        v
评价保存 --> 黄金样本
```

### 知识库管理

| 功能 | 说明 |
|------|------|
| 理论卡片 | 查看、搜索、添加、删除社会科学理论卡片 |
| 历史资料 | 管理历史事件记录，支持时期筛选 |
| 添加卡片 | 手动添加理论卡片或历史资料 |
| 批量导入 | 通过JSON文件批量导入数据 |

### 文档导入分析

支持格式：
- PDF文档 (.pdf)
- Word文档 (.docx)
- 纯文本文件 (.txt)

处理流程：
1. 上传文档
2. 选择处理模式 (AI自动分析/简单分割/手动处理)
3. 预览生成的知识卡片
4. 确认导入到知识库

---

## 知识库内容

### 理论卡片统计

| 类别 | 数量 | 主要内容 |
|------|------|----------|
| 马克思主义 | 48张 | 共产党宣言、资本论、德意志意识形态、哥达纲领批判等 |
| 列宁主义 | 8张 | 国家与革命、帝国主义论、怎么办、唯物主义和经验批判主义 |
| 毛泽东思想 | 27张 | 实践论、矛盾论、论持久战、论人民民主专政等 |
| 西方社会学 | 90张 | 韦伯、涂尔干、布迪厄、福柯、哈贝马斯等经典理论 |
| **总计** | **173张** | |

### 历史资料统计

| 时期 | 数量 | 主要内容 |
|------|------|----------|
| 古代文明 | 12条 | 美索不达米亚、古埃及、古希腊、古罗马、夏商周等 |
| 中世纪 | 3条 | 欧洲中世纪、伊斯兰文明、蒙古帝国 |
| 近代史 | 10条 | 文艺复兴、宗教改革、工业革命、法国大革命、鸦片战争等 |
| 现代史 | 14条 | 十月革命、世界大战、冷战、改革开放等 |
| **总计** | **39条** | |

---

## 配置说明

### 环境变量配置

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | 是 | - | DeepSeek API密钥 |
| `DEEPSEEK_BASE_URL` | 否 | `https://api.deepseek.com` | API服务地址 |
| `LLM_MODEL` | 否 | `deepseek-chat` | 使用的模型名称 |
| `LLM_TEMPERATURE` | 否 | `0.7` | 生成温度 (0.0-1.0) |
| `MAX_INPUT_LENGTH` | 否 | `10000` | 最大输入字符数 |
| `MAX_RETRIEVAL_RESULTS` | 否 | `10` | 默认检索结果数 |
| `MAX_RETRIEVAL_LIMIT` | 否 | `50` | 检索结果上限 |
| `MAX_HISTORY_RESULTS` | 否 | `5` | 历史资料检索数 |
| `HF_ENDPOINT` | 否 | `https://hf-mirror.com` | HuggingFace镜像地址 |

### 支持的LLM模型

- `deepseek-chat` - DeepSeek对话模型 (推荐)
- `deepseek-reasoner` - DeepSeek推理模型

---

## 开发计划

### 已完成功能

- [x] 基础RAG架构
- [x] 知识库管理
- [x] 理论分析功能
- [x] 历史资料库
- [x] 双模式分析
- [x] 文档导出
- [x] AI自动分析
- [x] 批量导入

### 计划功能

- [ ] 支持更多LLM模型 (OpenAI, Claude等)
- [ ] 分析历史记录
- [ ] 检索性能优化
- [ ] 多语言支持
- [ ] API接口开放
- [ ] 知识图谱可视化

---

## 开发者信息

<div align="center">

**北域工作室**

Northland Comprehensive Studio

---

[官网](https://beiyu.xuanjian.top/) | [GitHub](https://github.com/northland-studio/buceng-rag)

---

本项目为闭源项目，保留所有权利

</div>

---

<div align="center">

**不曾社科理论RAG分析系统**

让社会科学理论分析更智能

</div>
