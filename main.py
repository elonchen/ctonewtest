import os
import time
import uuid
import asyncio
import random
import json
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn


app = FastAPI(title="Local OpenAI Compatible API", version="1.0.0")

API_KEY = os.getenv("API_KEY", "sk-local-test-key")


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0


class CompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[str]]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 16
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0


class EmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
    encoding_format: Optional[str] = "float"


def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token


@app.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4",
                "parent": None,
            },
            {
                "id": "gpt-4-turbo",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4-turbo",
                "parent": None,
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-3.5-turbo",
                "parent": None,
            },
            {
                "id": "text-embedding-ada-002",
                "object": "model",
                "created": 1671217299,
                "owned_by": "openai",
                "permission": [],
                "root": "text-embedding-ada-002",
                "parent": None,
            },
            {
                "id": "text-davinci-003",
                "object": "model",
                "created": 1669599635,
                "owned_by": "openai",
                "permission": [],
                "root": "text-davinci-003",
                "parent": None,
            }
        ]
    }


def generate_mock_response(messages: List[Message], model: str) -> str:
    last_message = messages[-1].content if messages else ""
    
    responses = [
        f"这是一个模拟的 {model} 响应。您的问题是: {last_message[:50]}",
        f"我是一个本地模拟的 AI 助手。您提到: {last_message[:50]}...",
        f"感谢您使用本地 OpenAI 兼容 API。关于您的询问: {last_message[:50]}...",
    ]
    
    return random.choice(responses)


async def generate_chat_stream(request: ChatCompletionRequest):
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    
    mock_response = generate_mock_response(request.messages, request.model)
    words = mock_response.split()
    
    for i, word in enumerate(words):
        chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": word + " "} if i > 0 else {"role": "assistant", "content": word + " "},
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)
    
    final_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    if request.stream:
        return StreamingResponse(
            generate_chat_stream(request),
            media_type="text/event-stream"
        )
    
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    mock_response = generate_mock_response(request.messages, request.model)
    
    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": mock_response
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
            "completion_tokens": len(mock_response.split()),
            "total_tokens": sum(len(m.content.split()) for m in request.messages) + len(mock_response.split())
        }
    }


async def generate_completion_stream(request: CompletionRequest):
    completion_id = f"cmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    
    prompt = request.prompt if isinstance(request.prompt, str) else " ".join(request.prompt)
    mock_response = f"这是对提示词 '{prompt[:30]}...' 的模拟完成响应。"
    words = mock_response.split()
    
    for word in words:
        chunk = {
            "id": completion_id,
            "object": "text_completion",
            "created": created,
            "model": request.model,
            "choices": [
                {
                    "text": word + " ",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)
    
    final_chunk = {
        "id": completion_id,
        "object": "text_completion",
        "created": created,
        "model": request.model,
        "choices": [
            {
                "text": "",
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }
        ]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/completions")
async def create_completion(
    request: CompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    if request.stream:
        return StreamingResponse(
            generate_completion_stream(request),
            media_type="text/event-stream"
        )
    
    completion_id = f"cmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    
    prompt = request.prompt if isinstance(request.prompt, str) else " ".join(request.prompt)
    mock_response = f"这是对提示词 '{prompt[:30]}...' 的模拟完成响应。"
    
    return {
        "id": completion_id,
        "object": "text_completion",
        "created": created,
        "model": request.model,
        "choices": [
            {
                "text": mock_response,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(mock_response.split()),
            "total_tokens": len(prompt.split()) + len(mock_response.split())
        }
    }


@app.post("/v1/embeddings")
async def create_embedding(
    request: EmbeddingRequest,
    api_key: str = Depends(verify_api_key)
):
    inputs = request.input if isinstance(request.input, list) else [request.input]
    
    embeddings = []
    for idx, text in enumerate(inputs):
        embedding = [random.uniform(-1, 1) for _ in range(1536)]
        embeddings.append({
            "object": "embedding",
            "embedding": embedding,
            "index": idx
        })
    
    total_tokens = sum(len(text.split()) for text in inputs)
    
    return {
        "object": "list",
        "data": embeddings,
        "model": request.model,
        "usage": {
            "prompt_tokens": total_tokens,
            "total_tokens": total_tokens
        }
    }


@app.get("/")
async def root():
    return {
        "message": "OpenAI Compatible API Server",
        "version": "1.0.0",
        "endpoints": [
            "/v1/models",
            "/v1/chat/completions",
            "/v1/completions",
            "/v1/embeddings"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting OpenAI Compatible API Server on {host}:{port}")
    print(f"API Key: {API_KEY}")
    print(f"Documentation available at http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)
