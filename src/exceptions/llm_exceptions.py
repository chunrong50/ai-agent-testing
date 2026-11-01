import pytest
from src.llm.llm_client import LLMClient


class LLMServiceError(Exception):
    pass


class LLMTimeoutError(LLMServiceError):
    """自定义模型接口超时错误（项目里应已有类似定义）"""
    pass

class LLMServerError(LLMServiceError):
    """模拟底层 SDK 的服务端异常，带 status_code"""
    def __init__(self, status_code=500,message="Internal Server Error"):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


