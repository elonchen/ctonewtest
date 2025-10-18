#!/usr/bin/env python3
"""
使用官方 OpenAI SDK 与本地 API 交互的示例
需要安装: pip install openai
"""

try:
    import openai
except ImportError:
    print("请先安装 OpenAI SDK: pip install openai")
    exit(1)

# 配置 API
openai.api_key = "sk-local-test-key"
openai.api_base = "http://localhost:8000/v1"


def example_chat_completion():
    """聊天补全示例"""
    print("\n=== 聊天补全示例 ===")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "什么是机器学习？"}
        ]
    )
    
    print(f"回复: {response.choices[0].message.content}")
    print(f"Token 使用: {response.usage}")


def example_chat_completion_stream():
    """流式聊天补全示例"""
    print("\n=== 流式聊天补全示例 ===")
    
    stream = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "讲一个关于机器人的故事"}
        ],
        stream=True
    )
    
    print("流式响应: ", end="")
    for chunk in stream:
        if chunk.choices[0].delta.get("content"):
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")


def example_text_completion():
    """文本补全示例"""
    print("\n=== 文本补全示例 ===")
    
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="人工智能的三大要素是：",
        max_tokens=100
    )
    
    print(f"补全: {response.choices[0].text}")


def example_embeddings():
    """嵌入向量示例"""
    print("\n=== 嵌入向量示例 ===")
    
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input="这是一段测试文本"
    )
    
    embedding = response.data[0].embedding
    print(f"向量维度: {len(embedding)}")
    print(f"前10个值: {embedding[:10]}")


def example_list_models():
    """列出模型示例"""
    print("\n=== 列出可用模型 ===")
    
    models = openai.Model.list()
    
    print("可用模型:")
    for model in models.data:
        print(f"  - {model.id}")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("OpenAI SDK 使用示例")
    print("=" * 60)
    
    try:
        example_list_models()
        example_chat_completion()
        example_chat_completion_stream()
        example_text_completion()
        example_embeddings()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保:")
        print("1. 服务器正在运行: python main.py")
        print("2. API 密钥正确")
        print("3. 已安装 OpenAI SDK: pip install openai")


if __name__ == "__main__":
    main()
