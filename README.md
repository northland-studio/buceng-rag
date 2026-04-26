# Minecraft游戏社科分析台

## 项目简介

Minecraft游戏社科分析台是一个基于RAG（检索增强生成）架构的Web应用，旨在帮助研究人员分析Minecraft游戏内的社会学现象。系统结合本地向量知识库和云端大模型API，在保证数据安全的前提下，提供强大的理论分析能力。

## 功能特性

- 智能理论检索：自动从本地知识库检索相关社科理论
- AI分析生成：基于DeepSeek大模型生成专业分析报告
- 理论引用追踪：自动识别并展示引用的理论卡片
- 黄金样本管理：支持评分和保存高质量分析样本
- 本地数据安全：向量库和嵌入模型完全本地运行
- 友好Web界面：基于Streamlit的交互式界面

## 技术栈

- Python 3.10+
- Streamlit：Web框架
- ChromaDB：向量数据库
- sentence-transformers：嵌入模型
- OpenAI SDK：LLM API调用
- pydantic：数据验证

## 项目结构

```
beiyusocialer/
├── config.py              # 配置管理
├── logger.py              # 日志系统
├── exceptions.py          # 自定义异常
├── embedding.py           # 嵌入模型
├── knowledge_base.py      # 知识库管理
├── llm_api.py             # LLM API调用
├── utils.py               # 工具函数
├── app.py                 # Streamlit主界面
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例
├── data/                  # 数据目录
│   └── seed_cards.json    # 初始理论卡片
├── tests/                 # 测试目录
│   ├── test_utils.py
│   ├── test_config.py
│   └── test_exceptions.py
├── logs/                  # 日志目录
├── chroma_db/             # ChromaDB数据目录
├── Plan.md                # 开发计划
├── Reporter.md            # 开发报告
└── README.md              # 项目说明
```

## 快速开始

### 1. 环境准备

确保已安装Python 3.10或更高版本：

```bash
python --version
```

### 2. 克隆项目

```bash
git clone git@github.com:northland-studio/beiyusocialer.git
cd beiyusocialer
```

或

```bash
git clone git@gitee.com:northland_studio/beiyusocialer.git
cd beiyusocialer
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑`.env`文件，填写必要的配置：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 5. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址为`http://localhost:8501`。

## 使用指南

### 主界面功能

1. **事件输入**：在文本框中输入游戏内的事件描述
2. **提交分析**：点击"提交分析"按钮生成报告
3. **查看结果**：分析结果将显示在下方，引用部分会高亮显示
4. **评分保存**：对分析结果评分并保存为黄金样本

### 侧边栏功能

1. **知识库统计**：查看当前卡片数量和黄金样本数
2. **添加卡片**：手动添加新的理论卡片
3. **批量导入**：上传JSON文件批量导入卡片
4. **检索测试**：测试理论卡片检索功能

### 卡片格式

理论卡片JSON格式示例：

```json
{
  "id": "theory_001",
  "title": "理论标题",
  "content": "理论内容描述",
  "keywords": ["关键词1", "关键词2"],
  "source": "理论来源"
}
```

## 配置说明

### 必需配置

- `DEEPSEEK_API_KEY`：DeepSeek API密钥（必需）

### 可选配置

- `DEEPSEEK_BASE_URL`：API地址（默认：https://api.deepseek.com）
- `EMBEDDING_MODEL_NAME`：嵌入模型名称（默认：BAAI/bge-large-zh-v1.5）
- `EMBEDDING_DEVICE`：运行设备（默认：cpu，可选：cuda）
- `CHROMA_PERSIST_DIR`：ChromaDB数据目录（默认：./chroma_db）
- `MAX_INPUT_LENGTH`：最大输入长度（默认：5000）
- `LLM_TEMPERATURE`：LLM温度参数（默认：0.3）
- `LOG_LEVEL`：日志级别（默认：INFO）

## 测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定测试

```bash
pytest tests/test_utils.py
```

### 查看测试覆盖率

```bash
pytest --cov=. tests/
```

## 开发指南

### 代码风格

项目使用以下工具保证代码质量：

- black：代码格式化
- flake8：代码检查
- mypy：类型检查

运行代码检查：

```bash
black .
flake8 .
mypy .
```

### 添加新功能

1. 在相应模块中实现功能
2. 添加单元测试
3. 更新文档
4. 提交代码

## 部署指南

### Docker部署（推荐）

创建Dockerfile：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建并运行：

```bash
docker build -t beiyusocialer .
docker run -p 8501:8501 --env-file .env beiyusocialer
```

### 本地部署

直接运行：

```bash
streamlit run app.py
```

## 常见问题

### 1. 嵌入模型下载失败

**问题**：首次运行时模型下载失败或速度很慢。

**解决方案**：
- 使用国内镜像源
- 手动下载模型文件到本地
- 设置`HF_ENDPOINT`环境变量

### 2. API调用失败

**问题**：DeepSeek API调用失败。

**解决方案**：
- 检查API密钥是否正确
- 检查网络连接
- 查看API配额是否用尽

### 3. 内存不足

**问题**：运行时内存占用过高。

**解决方案**：
- 使用更小的嵌入模型
- 减少批处理大小
- 使用GPU加速

## 性能优化

### 1. 使用GPU加速

修改`.env`文件：

```env
EMBEDDING_DEVICE=cuda
```

### 2. 调整检索数量

在界面中调整"检索数量"参数，减少返回的理论卡片数量。

### 3. 使用缓存

Streamlit会自动缓存模型和知识库实例，无需额外配置。

## 安全建议

1. **保护API密钥**：不要将`.env`文件提交到版本控制
2. **定期备份**：定期备份`chroma_db`和`data`目录
3. **访问控制**：在生产环境中添加用户认证
4. **日志监控**：定期检查日志文件

## 项目状态

当前版本：v1.0.0

开发状态：核心功能已完成，测试中

## 更新日志

### v1.0.0 (2026-04-26)

- 完成核心功能开发
- 实现Web界面
- 添加单元测试
- 编写项目文档

## 贡献指南

欢迎提交Issue和Pull Request。

### 提交代码

1. Fork本项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 提交信息规范

- feat: 新增功能
- doc: 文档变更
- fix: 修复bug
- refactor: 代码重构
- perf: 性能优化
- test: 测试变更

## 许可证

本项目采用MIT许可证。

## 联系方式

- GitHub: https://github.com/northland-studio/beiyusocialer
- Gitee: https://gitee.com/northland_studio/beiyusocialer

## 致谢

感谢以下开源项目：

- Streamlit
- ChromaDB
- sentence-transformers
- OpenAI Python SDK
- pydantic
