from app.services.llm.minimax import MiniMaxLLM


class RAGService:
    def __init__(self):
        self.llm = MiniMaxLLM()

    async def generate(self, query: str, docs: list[str]) -> str:
        context = "\n".join(docs)

        prompt = f"""
请基于以下内容回答问题：

{context}

问题：
{query}
"""

        return await self.llm.chat([
            {"role": "user", "content": prompt}
        ])