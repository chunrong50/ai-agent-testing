from rag.rag_demo import RAG
import json
from pathlib import Path

PROMPT_PATH = ( Path(__file__).resolve().parents[2]
                / "prompts"
                / "payment_agent_system.txt"
                )

RULES_PATH = ( Path(__file__).resolve().parents[2]
                / "prompts"
                / "refund_rules.txt"
                )

CASES_PATH = ( Path(__file__).resolve().parents[2]
                / "datasets"
                / "day24_rag_cases.json"
                )


def test_01_rag_works_on_text(llm_openai,prompt):
    rag=RAG(llm_openai)

    raw_text = """
    公司内部出差报销标准：
    1. 一线城市（北京、上海、广州、深圳）住宿费标准为每晚 500 元。
    2. 二线城市住宿费标准为每晚 350 元。
    3. 高铁二等座按实际发生额报销，飞机票需提前 3 天预订方可全额报销。
    4. 餐饮补贴统一为每人每天 100 元，无需提供发票。
    """
    rag_chain=rag.run_mini_rag(raw_text=raw_text,prompt=prompt())

    # 设计测试用例进行提问
    test_questions = [
        # "请问去深圳出差，住宿费标准是多少？",
        # "飞机票有什么报销要求？",
        # "住深圳一晚给报销多少？",  # 口语话的问题
        "去三亚旅游住宿能报多少钱？"  # 故意设计一个知识库里完全没有的陷阱问题，测试幻觉拦截
    ]

    for q in test_questions:
        print(f"\n==============================")
        print(f"用户提问: {q}")
        response = rag_chain.invoke({"input": q})
        print(f"AI 回答: {response['answer']}")



def test_02_rag_works_on_json_case(llm_openai,prompt):
    rag=RAG(llm_openai)
    data=""
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 系统prompt
    system_prompt= PROMPT_PATH.read_text(encoding="utf-8")
    # refund_business_rules
    raw_text=RULES_PATH.read_text(encoding="utf-8")

    # rag chain
    rag_chain=rag.run_mini_rag(raw_text=raw_text,prompt=prompt(system_prompt))

    case1=data["test_cases"][1]["question"]
    print(f"用户提问: {case1}")
    response =rag_chain.invoke({"input": case1})
    print(f"AI 回答: {response['answer']}")

    assert "可以申请退货退款" in response





