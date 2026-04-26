# 模型下载问题解决方案

## 问题描述

由于网络原因，国内用户可能无法直接访问Hugging Face下载嵌入模型，会出现以下错误：

```
[WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。
```

## 解决方案

### 方案1：使用国内镜像源（推荐）

#### 方法1：修改配置文件

在`.env`文件中添加或修改以下配置：

```env
HF_ENDPOINT=https://hf-mirror.com
```

#### 方法2：使用启动脚本

**Windows用户**：
双击运行 `run_with_mirror.bat`

**Linux/Mac用户**：
```bash
chmod +x run_with_mirror.sh
./run_with_mirror.sh
```

### 方案2：手动下载模型

#### 步骤1：下载模型文件

访问国内镜像源下载模型：

**HF-Mirror（推荐）**：
https://hf-mirror.com/BAAI/bge-large-zh-v1.5

**ModelScope**：
https://modelscope.cn/models/Xorbits/bge-large-zh-v1.5

需要下载的文件：
- `config.json`
- `pytorch_model.bin`（约1.3GB）
- `tokenizer.json`
- `tokenizer_config.json`
- `special_tokens_map.json`
- `vocab.txt`
- `modules.json`（如果有）
- `sentence_bert_config.json`（如果有）

#### 步骤2：放置模型文件

将下载的文件放到本地目录，例如：
```
H:\chengxuyuanma\BUCENG\models\bge-large-zh-v1.5\
```

#### 步骤3：修改配置

在`.env`文件中修改模型路径：

```env
EMBEDDING_MODEL_NAME=./models/bge-large-zh-v1.5
```

或使用绝对路径：

```env
EMBEDDING_MODEL_NAME=H:/chengxuyuanma/BUCENG/models/bge-large-zh-v1.5
```

### 方案3：使用更小的模型

如果网络带宽有限，可以使用更小的模型：

#### 选项1：bge-small-zh（推荐）

```env
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.0
```

模型大小：约100MB

#### 选项2：bge-base-zh

```env
EMBEDDING_MODEL_NAME=BAAI/bge-base-zh-v1.5
```

模型大小：约400MB

### 方案4：使用代理

如果您有代理服务，可以设置环境变量：

#### Windows（PowerShell）

```powershell
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"
streamlit run app.py
```

#### Linux/Mac

```bash
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
streamlit run app.py
```

### 方案5：使用已缓存的模型

如果之前成功下载过模型，模型会缓存在：

**Windows**：
```
C:\Users\你的用户名\.cache\huggingface\hub\models--BAAI--bge-large-zh-v1.5
```

**Linux/Mac**：
```
~/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5
```

您可以：
1. 备份这个目录
2. 在其他机器上复制到相同位置
3. 无需重新下载

## 验证模型加载

启动应用后，查看日志文件 `logs/app_YYYYMMDD.log`，应该看到：

```
INFO - embedding.py - 正在加载嵌入模型: BAAI/bge-large-zh-v1.5
INFO - embedding.py - 使用Hugging Face镜像源: https://hf-mirror.com
INFO - embedding.py - 嵌入模型加载成功，向量维度: 1024
```

## 常见问题

### Q1: 下载速度很慢怎么办？

**A**: 使用HF-Mirror镜像源，下载速度会快很多。如果还是很慢，建议使用方案2手动下载。

### Q2: 模型加载失败怎么办？

**A**: 检查以下几点：
1. 模型文件是否完整下载
2. 文件路径是否正确
3. 是否有读取权限
4. 查看日志文件中的详细错误信息

### Q3: 内存不足怎么办？

**A**: 
1. 使用更小的模型（bge-small-zh）
2. 关闭其他应用程序
3. 增加虚拟内存

### Q4: 如何确认模型是否正确加载？

**A**: 在应用中输入测试文本进行分析，如果能看到分析结果，说明模型加载成功。

## 技术支持

如果以上方案都无法解决问题，请：

1. 查看日志文件：`logs/app_YYYYMMDD.log`
2. 查看错误日志：`logs/error_YYYYMMDD.log`
3. 提交Issue到GitHub仓库，附上日志文件

## 相关链接

- Hugging Face镜像：https://hf-mirror.com
- ModelScope：https://modelscope.cn
- BGE模型主页：https://huggingface.co/BAAI/bge-large-zh-v1.5
- 项目GitHub：https://github.com/northland-studio/beiyusocialer
