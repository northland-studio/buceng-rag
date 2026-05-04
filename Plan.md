# 不曾社科理论RAG分析系统 - 开发计划

<p align="center">
  <img src="logo.png" alt="BucengRAG Logo" width="150">
</p>

**开发者**: 北域工作室 (Northland Comprehensive Studio)  
**官网**: https://beiyu.xuanjian.top/

---

## 一、项目信息

| 项目名称 | 不曾社科理论RAG分析系统 |
|----------|------------------------|
| 英文名称 | Buceng Social Science RAG Analysis System |
| 开发者 | 北域工作室 (Northland Comprehensive Studio) |
| 技术架构 | RAG (Retrieval Augmented Generation) |
| 前端框架 | Streamlit |
| 向量数据库 | ChromaDB |
| 嵌入模型 | BAAI/bge-large-zh-v1.5 |
| LLM | DeepSeek API |

---

## 二、开发阶段

### 阶段一: 基础架构搭建 [已完成]

- [x] 项目结构设计
- [x] 配置管理模块
- [x] 日志系统
- [x] 异常处理
- [x] 向量嵌入模块
- [x] ChromaDB集成

### 阶段二: 核心功能开发 [已完成]

- [x] 知识库管理模块
- [x] LLM API封装
- [x] 理论卡片检索
- [x] 分析报告生成
- [x] 流式输出支持

### 阶段三: 用户界面开发 [已完成]

- [x] Streamlit主界面
- [x] 知识库管理页面
- [x] 文档导入分析页面
- [x] 系统设置页面
- [x] 自定义CSS样式

### 阶段四: 知识库建设 [已完成]

- [x] 马列毛理论卡片导入 (48张)
- [x] 社会科学理论卡片导入 (90张)
- [x] 人类文明历史资料导入 (39条)
- [x] 黄金样本功能

### 阶段五: 功能增强 [已完成]

- [x] 历史资料库功能
- [x] 双模式分析 (Minecraft/普通社科)
- [x] 文档导出 (MD/DOCX)
- [x] AI自动文档分析
- [x] 批量导入功能

---

## 三、模块清单

### 3.1 核心模块

| 模块 | 文件 | 状态 |
|------|------|------|
| 主应用 | app.py | 完成 |
| 配置管理 | config.py | 完成 |
| 知识库 | knowledge_base.py | 完成 |
| LLM接口 | llm_api.py | 完成 |
| 向量嵌入 | embedding.py | 完成 |
| 文档处理 | document_processor.py | 完成 |
| 文档导出 | document_exporter.py | 完成 |
| AI分析 | ai_analyzer.py | 完成 |
| 工具函数 | utils.py | 完成 |
| 日志系统 | logger.py | 完成 |
| 异常定义 | exceptions.py | 完成 |

### 3.2 数据文件

| 数据 | 文件 | 数量 |
|------|------|------|
| 社科理论卡片 | social_theory_cards.json | 20张 |
| 马列毛理论 | marxism_leninism_mao_cards.json | 48张 |
| 通用社科理论 | general_social_theory_cards.json | 90张 |
| 人类文明历史 | human_civilization_history.json | 39条 |

### 3.3 工具脚本

| 脚本 | 功能 |
|------|------|
| import_social_theory_cards.py | 导入社科理论卡片 |
| import_marxism_cards.py | 导入马列毛理论 |
| import_general_theory_cards.py | 导入通用社科理论 |
| import_history_records.py | 导入历史资料 |
| list_sources.py | 列出来源统计 |
| delete_cards_by_source.py | 按来源删除卡片 |

---

## 四、功能清单

### 4.1 分析功能

- [x] Minecraft游戏分析模式
- [x] 普通社科分析模式
- [x] 理论卡片检索
- [x] 历史资料检索
- [x] 流式输出
- [x] 引用标注

### 4.2 知识库功能

- [x] 理论卡片管理
- [x] 历史资料管理
- [x] 添加卡片 (理论/历史)
- [x] 批量导入 (理论/历史)
- [x] 搜索检索
- [x] 删除功能

### 4.3 文档功能

- [x] PDF文档解析
- [x] DOCX文档解析
- [x] TXT文本解析
- [x] AI自动分析
- [x] 知识卡片生成

### 4.4 导出功能

- [x] Markdown导出
- [x] Word文档导出
- [x] 生成信息标注
- [x] 理论引用记录

---

## 五、配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| DEEPSEEK_API_KEY | - | API密钥 |
| DEEPSEEK_BASE_URL | https://api.deepseek.com | API地址 |
| LLM_MODEL | deepseek-chat | 模型名称 |
| LLM_TEMPERATURE | 0.7 | 生成温度 |
| MAX_INPUT_LENGTH | 10000 | 最大输入长度 |
| MAX_RETRIEVAL_RESULTS | 10 | 检索结果数 |
| MAX_RETRIEVAL_LIMIT | 50 | 检索上限 |
| MAX_HISTORY_RESULTS | 5 | 历史资料检索数 |
| HF_ENDPOINT | https://hf-mirror.com | HF镜像 |

---

## 六、未来规划

### 6.1 短期目标

- [ ] 支持更多LLM模型 (OpenAI, Claude等)
- [ ] 增加分析历史记录
- [ ] 优化检索性能
- [ ] 增加用户反馈机制

### 6.2 中期目标

- [ ] 多语言支持
- [ ] 理论卡片自动更新
- [ ] 协作分析功能
- [ ] API接口开放

### 6.3 长期目标

- [ ] 移动端适配
- [ ] 离线部署方案
- [ ] 企业版功能
- [ ] 知识图谱可视化

---

## 七、版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-05 | 初始版本发布 |
| v1.1 | 2026-05 | 添加历史资料库功能 |
| v1.2 | 2026-05 | 添加双模式分析 |
| v1.3 | 2026-05 | 添加文档导出功能 |
| v1.4 | 2026-05 | 品牌更新，添加logo |

---

## 八、开发团队

**北域工作室** (Northland Comprehensive Studio)

- 官网: https://beiyu.xuanjian.top/
- 项目地址: https://github.com/northland-studio/buceng-rag

本项目为闭源项目，保留所有权利

---

<p align="center">
  <strong>不曾社科理论RAG分析系统</strong><br>
  让社会科学理论分析更智能
</p>
