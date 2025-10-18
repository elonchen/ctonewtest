# 快速开始指南

## 5 分钟上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

或使用启动脚本：

```bash
./start.sh
```

### 3. 测试 API

打开新的终端窗口：

```bash
# 方式 1: 使用测试脚本
python test_api.py

# 方式 2: 使用 curl
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer sk-local-test-key"
```

## 验证安装

访问 http://localhost:8000/docs 查看交互式 API 文档。

## 下一步

- 查看 [README.md](README.md) 了解完整文档
- 运行 `python test_api.py` 测试所有端点
- 查看 `example_openai_sdk.py` 了解如何使用 OpenAI SDK

## 常见问题

### 端口被占用

修改端口：

```bash
export PORT=3000
python main.py
```

### 修改 API 密钥

```bash
export API_KEY=your-custom-key
python main.py
```

### Docker 运行

```bash
docker build -t openai-local .
docker run -p 8000:8000 openai-local
```

## 支持

遇到问题？请查看 [README.md](README.md) 的常见问题部分。
