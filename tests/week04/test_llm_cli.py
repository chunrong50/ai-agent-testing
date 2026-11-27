
import logging

from llm.llm_cli import LLMCLI

logger = logging.getLogger(__name__)

def test_01_llm_cli():
    # 多轮对话
    agent=LLMCLI()
    logger.info("开始控制台与AI对话吧，请先输入您的问题")
    agent.run_chat_cli()

def test_02_llm_single_turn():
    # 单论对话
    agent=LLMCLI()
    test_prompt = "请用简练的语言概况 AI Agent 测试最重要的指标有哪些？"
    logger.info(f"正在向大模型发送请求...\n输入: {test_prompt}\n")

    result=agent.ask_ai_single_turn(test_prompt)

    logger.info(f"大模型输出:\n{result}")
