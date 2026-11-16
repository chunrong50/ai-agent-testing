# 设计 4 个高价值测试
# 测试	验证目标
# TC01	正常添加并读取 Memory
# TC02	不同 user_id 的 Memory 相互隔离
# TC03	更新 Memory 后读取到最新内容
# TC04	删除 Memory 后无法再次读取
from agent.memory import ShortTermMemory, build_context


def test_01_normal_add_and_retrieve_memory():
    short=ShortTermMemory()
    short.add_message("user","帮我查询订单A10086")
    short.add_message("assistant","订单A10086已经支付，未退款")

    short.update_context("user","帮我查询订单A10086")
    short.update_context("order_id","A10086")
    short.update_context("assistant", "订单A10086已支付，未退款")
    short.update_context("order_status", "已支付，未退款")

    assert short.retrieve_context("order_id")=="A10086"
    assert short.retrieve_context("order_status")=="已支付，未退款"

    assert len(short.messages)==2
    assert short.messages[0]["role"]=="user"
    assert short.messages[1]["role"] == "assistant"





def test_02_different_memory_instances_are_isolated():
    short1 = ShortTermMemory()
    short1.add_message("user", "帮我查询订单A10086")


    short2 = ShortTermMemory()
    short2.add_message("user", "帮我查询订单A10087")

    short1.update_context("order_id", "A10086")
    short2.update_context("order_id", "A10087")

    assert short1.retrieve_context("order_id")=="A10086"
    assert short2.retrieve_context("order_id") == "A10087"


def test_03_update_memory_and_retrieve_latest_message():
    short1 = ShortTermMemory()
    short1.add_message("user", "帮我查询订单A10086")
    short1.update_context("order_id", "A10086")
    short1.update_context("order_id", "A10087")

    assert short1.retrieve_context("order_id")=="A10087"


def test_04_delete_memory_and_can_not_retrieve():
    short1 = ShortTermMemory()
    short1.add_message("user", "帮我查询订单A10086")
    short1.update_context("order_id", "A10086")

    short1.delete_context("order_id")

    assert short1.retrieve_context("order_id") is None

# Day 12

def test_day12_01_retrieval_accuracy():
    short1 = ShortTermMemory()
    short1.add_message("user", "帮我查询订单A10086")
    short1.add_message("assistant", "订单A10086已支付，未退款")
    short1.update_context("order_id", "A10086")
    short1.update_context("user_id", "U001")
    short1.update_context("order_status", "PAID")
    short1.update_context("language", "Chinese")

    context=build_context(short1, ["order_id", "user_id", "language"])

    assert context["user_id"]=="U001"
    assert context["order_id"]=="A10086"
    assert context["language"] == "Chinese"
    assert "order_status" not in context
