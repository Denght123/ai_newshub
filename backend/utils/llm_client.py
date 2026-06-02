import httpx


def build_chat_completions_url(api_base_url: str):
    base_url = api_base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


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
