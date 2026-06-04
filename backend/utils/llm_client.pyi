from collections.abc import AsyncIterator, Mapping, Sequence
from typing import TypedDict


class ChatMessageResponse(TypedDict):
    content: str


class ChatChoiceResponse(TypedDict):
    message: ChatMessageResponse


class ChatCompletionResponse(TypedDict):
    choices: list[ChatChoiceResponse]


class EmbeddingDataResponse(TypedDict):
    embedding: list[float]


class EmbeddingResponse(TypedDict):
    data: list[EmbeddingDataResponse]


def build_chat_completions_url(api_base_url: str) -> str: ...


def build_embeddings_url(api_base_url: str) -> str: ...


async def call_openai_compatible_chat(
    api_base_url: str,
    api_key: str,
    model: str,
    messages: Sequence[Mapping[str, str]],
) -> ChatCompletionResponse: ...


async def call_openai_compatible_embeddings(
    api_base_url: str,
    api_key: str,
    model: str,
    texts: Sequence[str],
) -> list[list[float]]: ...


def stream_openai_compatible_chat(
    api_base_url: str,
    api_key: str,
    model: str,
    messages: Sequence[Mapping[str, str]],
) -> AsyncIterator[str]: ...
