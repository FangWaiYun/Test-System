import typing
import json
import logging
import re
import httpx
from pydantic import BaseModel
from openai.types.chat import ChatCompletionMessageParam

from ..prompts.models import Message
from .config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
from .openai_base_client import BaseOpenAIClient

logger = logging.getLogger(__name__)

# 强烈建议放入 .env 环境变量
API_KEY = "sk-riqwntpzgjgbirvaoyhfkngephynfsuegejfzcefqmjazwbh"

def extract_json_block(text: str) -> str:
    """尝试直接验证是否为合法 JSON 字符串，失败时返回空对象。"""
    try:
        json.loads(text)
        return text  # 本身就是合法 JSON 字符串，直接返回
    except Exception:
        pass

    # 如果 text 是 markdown 包裹的 JSON，比如 ```json\n{...}\n```
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if match:
        block = match.group(1)
        try:
            json.loads(block)
            return block
        except Exception:
            pass

    # 如果是文本中间部分包裹的完整 JSON 对象
    candidates = re.findall(r'\{[\s\S]*?\}', text)
    for candidate in candidates:
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            continue

    # fallback：返回空 JSON
    return "{}"


class OllamaClient(BaseOpenAIClient):
    """
    A client for interacting with Ollama server-compatible LLMs using HTTP requests.
    """

    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
    ):
        super().__init__(config, cache)
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _create_structured_completion(
        self,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None,
        max_tokens: int,
        response_model: type[BaseModel],
    ):
        prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
        prompt += "\n\n请按照 JSON 格式输出结构化内容，确保符合以下 schema：\n"
        prompt += response_model.schema_json(indent=2)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature or 0.0,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
            )
            response.raise_for_status()
            result = response.json()
            raw = result["response"]

        try:
            json_str = extract_json_block(raw)
            return response_model.parse_raw(json_str)
        except Exception as e:
            logger.error(f"Ollama structured parse error: {e}\nRaw content:\n{raw}")
            raise

    async def _create_completion(
        self,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None,
        max_tokens: int,
        response_model: type[BaseModel] | None = None,
    ):
        prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature or 0.0,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
            )
            response.raise_for_status()
            result = response.json()

        return type("OllamaResponse", (), {"choices": [{"message": {"content": result["response"]}}]})

BASE_URL="https://api.siliconflow.cn/v1/chat/completions"
# 模拟 OpenAI 返回格式的对象
class Message:
    def __init__(self, content: str):
        self.content = content

class Choice:
    def __init__(self, message: Message):
        self.message = message

class CustomResponse:
    def __init__(self, choices: list[Choice]):
        self.choices = choices


class CustomAPIClient(BaseOpenAIClient):
    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        base_url: str = "https://api.siliconflow.cn/v1/chat/completions",
        model: str = "Qwen/QwQ-32B",
    ):
        super().__init__(config, cache)
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _create_structured_completion(
        self,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None,
        max_tokens: int,
        response_model: type[BaseModel],
    ):
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "请返回结构化 JSON 格式数据，符合以下 schema：\n" +
                               response_model.schema_json(indent=2)
                },
                *messages
            ],
            "temperature": temperature or 0.0,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                },
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            raw = result["choices"][0]["message"]["content"]
            print("🔵 Raw structured response:\n", raw)

        try:
            json_str = extract_json_block(raw)
            parsed_obj = response_model.parse_raw(json_str)

            # 关键：构造符合 Graphiti 预期结构的返回
            class ParsedMessage:
                def __init__(self, parsed):
                    self.parsed = parsed

            class StructuredResponse:
                def __init__(self, parsed):
                    self.choices = [type("Choice", (), {"message": ParsedMessage(parsed)})]

            return StructuredResponse(parsed_obj)

        except Exception as e:
            logger.error(f"CustomAPIClient structured parse error: {e}\nRaw content:\n{raw}")
            raise

    async def _create_completion(
        self,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None,
        max_tokens: int,
        response_model: type[BaseModel] | None = None,
    ):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or 0.0,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print("🟢 Raw chat response:\n", content)

        return CustomResponse([Choice(Message(content))])