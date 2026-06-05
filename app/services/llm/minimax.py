import httpx

from app.core.config import settings


class MiniMaxLLM:
    BASE_URL = "https://api.minimaxi.com/v1/text/chat"

    async def chat(self, messages: list[dict]) -> str:
        # 短路:MOCK 模式下返回固定答案,跳过网络和 API key
        if settings.LLM_MOCK:
            return _mock_response(messages)

        headers = {
            "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "MiniMax-M3",
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self.BASE_URL, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]


def _mock_response(messages: list[dict]) -> str:
    """离线/CI 用的假 LLM 回复。

    把最后一条 user message 的前 80 字符回显,方便人眼验证 pipeline 通畅。
    """
    last_user = next(
        (m for m in reversed(messages) if m.get("role") == "user"),
        None,
    )
    if not last_user:
        return "[MOCK LLM] 收到空消息"
    snippet = last_user["content"][:80].replace("\n", " ")
    return f"[MOCK LLM] 已收到 query,前 80 字:{snippet!r}(mock 模式不真生成)"