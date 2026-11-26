from functools import wraps

from mcp.client import Client
from mcp.server import Server
from tools.order_tool import OrderTool
from tools.refund_tool import RefundTool


def test_01_client_request_server_query_order(env):
    # ("query_order", "ORD1001")
    # query_order 被调用一次,execute_refund 没有被调用。

    server=Server(env["tools"])
    client=Client(server)

    from unittest.mock import Mock
    query_order=env["tools"]["query_order"]
    execute_tool=env["tools"]["execute_refund"]
    query_order.query_order=Mock(wraps=query_order.query_order)
    execute_tool.execute_refund = Mock(wraps=execute_tool.execute_refund)

    result=client.execute_tool("query_order",arg="ORD1001")

    assert result["data"]["order_id"]=="ORD1001"
    assert result["success"]==True

    assert query_order.query_order.call_count == 1
    assert execute_tool.execute_refund.call_count == 0







