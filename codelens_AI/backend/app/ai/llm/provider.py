from abc import ABC, abstractmethod
from typing import AsyncGenerator
import litellm

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list, temperature: float = 0.2, max_tokens: int | None = None) -> str:
        pass

    @abstractmethod
    async def stream(self, messages: list, temperature: float = 0.2, max_tokens: int | None = None) -> AsyncGenerator[str, None]:
        pass

class LiteLLMProvider(LLMProvider):
    def __init__(self, model_name: str, api_base: str | None = None):
        self.model_name = model_name
        self.api_base = api_base
        # Example for Ollama: model_name="ollama/qwen2.5:7b", api_base="http://localhost:11434"

    async def generate(self, messages: list, temperature: float = 0.2, max_tokens: int | None = None) -> str:
        response = await litellm.acompletion(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=self.api_base
        )
        return response.choices[0].message.content

    async def stream(self, messages: list, temperature: float = 0.2, max_tokens: int | None = None) -> AsyncGenerator[str, None]:
        response = await litellm.acompletion(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=self.api_base,
            stream=True
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
