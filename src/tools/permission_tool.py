
# src/tools/permission_tool.py

class PermissionTool:
    """用户订单操作权限校验工具。"""

    def check_permission(self,user_id: str,order: dict) -> dict:
        """验证用户是否有权操作指定订单。"""
        if not isinstance(user_id, str) or not user_id.strip():
            return {
                "success": False,
                "allowed": False,
                "error": "用户ID不能为空"
            }

        if not isinstance(order, dict):
            return {
                "success": False,
                "allowed": False,
                "error": "订单数据无效"
            }

        order_user_id = order.get("user_id")

        if not order_user_id:
            return {
                "success": False,
                "allowed": False,
                "error": "订单缺少所属用户信息"
            }

        allowed = user_id == order_user_id

        return {
            "success": True,
            "allowed": allowed,
            "user_id": user_id,
            "order_user_id": order_user_id,
            "reason": (
                "用户有权操作该订单"
                if allowed
                else "用户无权操作该订单"
            )
        }
