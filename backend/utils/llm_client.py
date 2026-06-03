import httpx


# 拼出聊天补全接口地址：兼容传入 base_url 或完整 /chat/completions 地址两种情况。
def build_chat_completions_url(api_base_url: str):
    base_url = api_base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


# 调用 OpenAI-compatible 大模型接口：传入 base_url、api_key、model 和 messages，返回模型原始 JSON。
async def call_openai_compatible_chat(
    api_base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
):
    url = build_chat_completions_url(api_base_url)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=payload)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            detail = response.text[:500]
            raise ValueError(f"LLM API request failed: {response.status_code} {detail}") from err
        return response.json()


# 流式调用 OpenAI-compatible 大模型接口：逐段产出 delta 文本，供 SSE 接口转发给前端。
async def stream_openai_compatible_chat(
    api_base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
):
    url = build_chat_completions_url(api_base_url)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as err:
                body = await response.aread()
                detail = body.decode("utf-8", errors="replace")[:500]
                raise ValueError(f"LLM stream request failed: {response.status_code} {detail}") from err

            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue

                data = line.removeprefix("data:").strip()
                if not data or data == "[DONE]":
                    continue

                yield data
