import os
from dotenv import load_dotenv
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from rag.qianwen_embedding import QwenEmbeddings

# 1. 加载环境变量
load_dotenv()


class RAG:

    def __init__(self,llm):
        self.llm = llm


    def run_mini_rag(self, raw_text,prompt):

        # 将文本封装为 LangChain 的 Document 对象
        docs = [Document(page_content=raw_text)]

        print("正在初始化嵌入模型并构建向量数据库...")
        # 3. 实例化 Embedding 模型（用于将文字转为向量）,下面是OPENAIEmbeddings, 千问的embedding不兼容
        # embeddings = OpenAIEmbeddings(
        #     model="text-embedding-v3",  # 也可以用开源的本地 Embedding
        #     api_key=os.getenv("OPENAI_API_KEY"),
        #     base_url=os.getenv("OPENAI_BASE_URL"),
        #     chunk_size=10
        # )
        embeddings = QwenEmbeddings(model="text-embedding-v3")

        # 4. 写入内存版向量数据库 Chroma
        vectorstore = Chroma.from_documents(docs, embeddings)

        # 5. 创建检索器（Retriever），设置每次召回最相关的 1 个片段
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 1}
        )

        #  组装 RAG 链 (Retrieval Chain)
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        return rag_chain




