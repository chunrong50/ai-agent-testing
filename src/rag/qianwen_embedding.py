
import os

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
import dashscope
from http import HTTPStatus

# 加载当前目录下的 .env 文件
load_dotenv()


# 设置你的阿里云百炼 API Key
dashscope.api_key = os.getenv("OPENAI_API_KEY")

class QwenEmbeddings(Embeddings):
    """自定义一个通义千问的 Embedding 类，完美兼容 LangChain 和 Chroma"""
    def __init__(self, model: str = "text-embedding-v3"):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # 调用官方 SDK 批量获取向量
        resp = dashscope.TextEmbedding.call(
            model=self.model,
            input=texts
        )
        if resp.status_code == HTTPStatus.OK:
            return [item['embedding'] for item in resp.output['embeddings']]
        else:
            raise Exception(f"DashScope Embedding Error: {resp.code} - {resp.message}")

    def embed_query(self, text: str) -> list[float]:
        # 获取单个查询文本的向量
        resp = dashscope.TextEmbedding.call(
            model=self.model,
            input=[text]
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.output['embeddings'][0]['embedding']
        else:
            raise Exception(f"DashScope Embedding Error: {resp.code} - {resp.message}")

