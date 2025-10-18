# 本地 OpenAI 兼容 API 服务

一个完全兼容 OpenAI API 规范的本地服务，使用 Python 和 FastAPI 实现，支持流式响应和 API 密钥验证。

## 功能特性

- ✅ **完整的 OpenAI API 兼容**：支持主要的 OpenAI API 端点
- ✅ **流式响应**：支持 SSE (Server-Sent Events) 流式输出
- ✅ **API 密钥验证**：Bearer Token 认证机制
- ✅ **模拟数据响应**：无需实际 AI 模型，返回模拟数据
- ✅ **自动文档**：FastAPI 自带的 Swagger UI 文档

## 支持的端点

1. `GET /v1/models` - 获取可用模型列表
2. `POST /v1/chat/completions` - 聊天补全（支持流式和非流式）
3. `POST /v1/completions` - 文本补全（支持流式和非流式）
4. `POST /v1/embeddings` - 文本嵌入向量
5. `GET /health` - 健康检查端点
6. `GET /` - API 信息

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件设置您的配置：

```
API_KEY=sk-local-test-key
HOST=0.0.0.0
PORT=8000
```

### 3. 启动服务

**方法 1：直接运行**

```bash
python main.py
```

**方法 2：使用 uvicorn**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，访问：
- API 服务：http://localhost:8000
- 交互式文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

## API 使用示例

### 使用 curl

#### 1. 获取模型列表

```bash
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer sk-local-test-key"
```

#### 2. 聊天补全（非流式）

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-test-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
  }'
```

#### 3. 聊天补全（流式）

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-test-key" \
  -N \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "讲一个故事"}
    ],
    "stream": true
  }'
```

#### 4. 文本补全

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-test-key" \
  -d '{
    "model": "text-davinci-003",
    "prompt": "从前有座山，",
    "max_tokens": 50
  }'
```

#### 5. 文本嵌入

```bash
curl http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-test-key" \
  -d '{
    "model": "text-embedding-ada-002",
    "input": "这是一段测试文本"
  }'
```

### 使用 Python (OpenAI SDK)

#### 安装 OpenAI SDK

```bash
pip install openai
```

#### Python 代码示例

```python
import openai

# 配置 API
openai.api_key = "sk-local-test-key"
openai.api_base = "http://localhost:8000/v1"

# 1. 聊天补全
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)
print(response.choices[0].message.content)

# 2. 流式聊天补全
stream = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "讲个故事"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta.content, end="")

# 3. 文本嵌入
embedding = openai.Embedding.create(
    model="text-embedding-ada-002",
    input="这是测试文本"
)
print(embedding.data[0].embedding[:5])  # 显示前5个维度

# 4. 获取模型列表
models = openai.Model.list()
for model in models.data:
    print(model.id)
```

### 使用 Python (requests 库)

```python
import requests
import json

base_url = "http://localhost:8000"
headers = {
    "Authorization": "Bearer sk-local-test-key",
    "Content-Type": "application/json"
}

# 聊天补全
response = requests.post(
    f"{base_url}/v1/chat/completions",
    headers=headers,
    json={
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)
print(response.json())

# 流式响应
response = requests.post(
    f"{base_url}/v1/chat/completions",
    headers=headers,
    json={
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "讲个故事"}
        ],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]
            if data != '[DONE]':
                print(data)
```

## API 参数说明

### Chat Completions

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| messages | array | 是 | 消息列表 |
| temperature | float | 否 | 温度参数 (0-2) |
| max_tokens | integer | 否 | 最大生成token数 |
| stream | boolean | 否 | 是否启用流式响应 |
| top_p | float | 否 | 核采样参数 |
| n | integer | 否 | 生成响应数量 |
| stop | string/array | 否 | 停止序列 |

### Completions

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| prompt | string/array | 是 | 提示词 |
| temperature | float | 否 | 温度参数 (0-2) |
| max_tokens | integer | 否 | 最大生成token数 |
| stream | boolean | 否 | 是否启用流式响应 |

### Embeddings

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| input | string/array | 是 | 输入文本 |
| encoding_format | string | 否 | 编码格式 |

## 错误处理

服务会返回标准的 HTTP 状态码：

- `200` - 请求成功
- `401` - 未授权（API密钥无效或缺失）
- `422` - 请求参数验证失败
- `500` - 服务器内部错误

### 401 错误示例

```bash
# 缺少 API 密钥
curl http://localhost:8000/v1/models

# 响应
{
  "detail": "Missing API key"
}

# 无效 API 密钥
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer wrong-key"

# 响应
{
  "detail": "Invalid API key"
}
```

## 配置说明

### 环境变量

- `API_KEY` - API 密钥，默认为 `sk-local-test-key`
- `HOST` - 服务监听地址，默认为 `0.0.0.0`
- `PORT` - 服务端口，默认为 `8000`

### 修改 API 密钥

**方法 1：环境变量**

```bash
export API_KEY=your-custom-key
python main.py
```

**方法 2：.env 文件**

创建 `.env` 文件：

```
API_KEY=your-custom-key
```

然后安装并使用 python-dotenv：

```python
from dotenv import load_dotenv
load_dotenv()
```

## 开发和调试

### 启用热重载

```bash
uvicorn main:app --reload
```

### 查看日志

服务会在控制台输出请求日志，包括：
- 启动信息
- 配置的 API 密钥
- 每个请求的详情

### 访问交互式文档

FastAPI 自动生成 Swagger UI 文档：

```
http://localhost:8000/docs
```

在文档页面可以：
- 查看所有端点
- 测试 API 调用
- 查看请求/响应模型

## 生产部署建议

1. **使用环境变量**：不要在代码中硬编码 API 密钥
2. **HTTPS**：在生产环境使用 HTTPS（通过 nginx 或其他反向代理）
3. **进程管理**：使用 systemd、supervisor 或 docker 管理服务进程
4. **日志管理**：配置日志输出到文件并设置日志轮转
5. **限流**：添加请求限流以防止滥用

### Docker 部署示例

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV API_KEY=sk-local-test-key
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
```

构建并运行：

```bash
docker build -t openai-api-local .
docker run -p 8000:8000 -e API_KEY=your-key openai-api-local
```

## 技术栈

- **FastAPI** - 现代、高性能的 Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证和设置管理
- **Python 3.8+** - 编程语言

## 许可证

MIT

## 注意事项

⚠️ 本服务返回的是**模拟数据**，不包含实际的 AI 模型。适用于：
- 开发和测试
- API 集成测试
- 演示和原型开发
- 学习 OpenAI API 规范

如需实际 AI 功能，请：
1. 集成真实的 AI 模型（如本地运行的 LLaMA、ChatGLM 等）
2. 或使用官方的 OpenAI API
3. 或集成其他 AI 服务提供商的 API

## 常见问题

### Q: 如何集成真实的 AI 模型？

A: 您可以修改 `generate_mock_response` 函数，将其替换为实际的模型推理代码。例如：

```python
def generate_mock_response(messages, model):
    # 替换为实际的模型调用
    # from transformers import pipeline
    # generator = pipeline('text-generation', model='your-model')
    # return generator(messages[-1].content)[0]['generated_text']
    pass
```

### Q: 支持哪些模型？

A: 当前支持的模型列表在 `/v1/models` 端点中定义。您可以在 `list_models` 函数中添加或删除模型。

### Q: 如何修改端口？

A: 使用环境变量 `PORT=3000 python main.py` 或在 `.env` 文件中设置。

### Q: API 密钥可以支持多个吗？

A: 当前实现只支持单个 API 密钥。如需支持多个密钥，可以修改 `verify_api_key` 函数：

```python
VALID_API_KEYS = ["sk-key-1", "sk-key-2", "sk-key-3"]

def verify_api_key(authorization: Optional[str] = Header(None)):
    # ... 验证逻辑
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 反馈。
