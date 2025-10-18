#!/usr/bin/env python3
"""
测试脚本：演示如何使用本地 OpenAI 兼容 API
使用 requests 库进行测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "sk-local-test-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_models():
    """测试模型列表端点"""
    print("\n=== 测试 /v1/models ===")
    response = requests.get(f"{BASE_URL}/v1/models", headers=headers)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"可用模型数量: {len(data['data'])}")
    for model in data['data']:
        print(f"  - {model['id']}")


def test_chat_completion():
    """测试聊天补全端点（非流式）"""
    print("\n=== 测试 /v1/chat/completions (非流式) ===")
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "请用一句话介绍 Python 编程语言"}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"模型: {data['model']}")
    print(f"响应内容: {data['choices'][0]['message']['content']}")
    print(f"Token 使用: {data['usage']}")


def test_chat_completion_stream():
    """测试聊天补全端点（流式）"""
    print("\n=== 测试 /v1/chat/completions (流式) ===")
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "讲一个关于人工智能的故事"}
        ],
        "stream": True
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers=headers,
        json=payload,
        stream=True
    )
    
    print(f"状态码: {response.status_code}")
    print("流式响应内容:")
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    print("\n[流式响应结束]")
                    break
                else:
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                print(delta['content'], end='', flush=True)
                    except json.JSONDecodeError:
                        pass


def test_completion():
    """测试文本补全端点"""
    print("\n=== 测试 /v1/completions ===")
    payload = {
        "model": "text-davinci-003",
        "prompt": "人工智能的未来是",
        "max_tokens": 50,
        "temperature": 0.8
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/completions",
        headers=headers,
        json=payload
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"模型: {data['model']}")
    print(f"补全内容: {data['choices'][0]['text']}")


def test_embeddings():
    """测试嵌入端点"""
    print("\n=== 测试 /v1/embeddings ===")
    payload = {
        "model": "text-embedding-ada-002",
        "input": "这是一段用于生成嵌入向量的测试文本"
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/embeddings",
        headers=headers,
        json=payload
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"模型: {data['model']}")
    print(f"嵌入向量维度: {len(data['data'][0]['embedding'])}")
    print(f"前10个值: {data['data'][0]['embedding'][:10]}")
    print(f"Token 使用: {data['usage']}")


def test_auth_failure():
    """测试 API 密钥验证失败"""
    print("\n=== 测试 API 密钥验证 ===")
    
    # 测试缺少密钥
    response = requests.get(f"{BASE_URL}/v1/models")
    print(f"缺少密钥 - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 测试无效密钥
    wrong_headers = {
        "Authorization": "Bearer wrong-key",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{BASE_URL}/v1/models", headers=wrong_headers)
    print(f"无效密钥 - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("本地 OpenAI 兼容 API 测试脚本")
    print("=" * 60)
    
    try:
        # 测试服务器是否可用
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 服务器未运行！请先启动服务器: python main.py")
            return
        
        print("✅ 服务器运行正常")
        
        # 运行测试
        test_models()
        test_chat_completion()
        test_chat_completion_stream()
        test_completion()
        test_embeddings()
        test_auth_failure()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器！请确保服务器正在运行: python main.py")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    main()
