# Python stdlib
# Project Dependencies
from dataclasses import dataclass

import litellm

# Project Imports


@dataclass
class LLMClientModelConfig:
    model_name: str
    max_tokens: int
    temperature: float
    extras: dict = None


class LLMClient:
    def __init__(self, model_config: LLMClientModelConfig):
        self.model_config = model_config

    def call_model(self, messages: list[dict]) -> str:
        response = litellm.completion(
            model=self.model_config.model_name,
            messages=messages,
            temperature=self.model_config.temperature,
            max_tokens=self.model_config.max_tokens,
        )
        return response.choices[0].message.content


if __name__ == "__main__":
    pass
