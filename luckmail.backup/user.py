"""
LuckMail User API
用户相关接口
"""

from typing import Any, Dict, Optional, List


class UserAPI:
    """用户 API"""

    def __init__(self, client):
        self.client = client

    def get_balance(self) -> Any:
        """获取账户余额"""
        return self.client.request('GET', 'user/info')

    def get_orders(self, page: int = 1, page_size: int = 20, status: Optional[int] = None, project_id: Optional[int] = None) -> Any:
        """
        获取订单列表

        Args:
            page: 页码
            page_size: 每页数量
            status: 订单状态 (1=待接码 2=已完成 3=已超时 4=已取消 5=已退款)
            project_id: 项目 ID

        Returns:
            订单列表
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        if status is not None:
            params['status'] = status
        if project_id is not None:
            params['project_id'] = project_id
        return self.client.request('GET', 'orders', params=params)

    def create_order(
        self,
        project_code: str,
        email_type: str = "",
        domain: Optional[str] = None,
        specified_email: Optional[str] = None
    ) -> Any:
        """
        创建订单

        Args:
            project_code: 项目代码
            email_type: 邮箱类型
            domain: 指定域名
            specified_email: 指定邮箱地址

        Returns:
            订单信息
        """
        data = {
            'project_code': project_code,
            'email_type': email_type or "",
            'domain': domain or "",
            'specified_email': specified_email or "",
            'variant_mode': ""
        }

        return self.client.request('POST', 'order/create', json=data)

    def get_order_code(self, order_no: str) -> Any:
        """
        获取订单验证码

        Args:
            order_no: 订单号

        Returns:
            验证码信息，包含 status, verification_code 等
            status: pending=待接码, success=成功, timeout=超时, cancelled=已取消
        """
        return self.client.request('GET', f'order/{order_no}/code')

    def cancel_order(self, order_no: str) -> Any:
        """
        取消订单

        Args:
            order_no: 订单号

        Returns:
            取消结果
        """
        return self.client.request('POST', f'order/{order_no}/cancel')

    def get_purchases(
        self,
        page: int = 1,
        page_size: int = 20,
        user_disabled: int = 0,
        project_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> Any:
        """
        获取已购邮箱列表

        Args:
            page: 页码
            page_size: 每页数量
            user_disabled: 是否禁用 (0=未禁用, 1=已禁用)
            project_id: 项目 ID
            tag_id: 标签 ID
            keyword: 邮箱地址关键词

        Returns:
            已购邮箱列表
        """
        params = {
            'page': page,
            'page_size': page_size,
            'user_disabled': user_disabled
        }
        if project_id is not None:
            params['project_id'] = project_id
        if tag_id is not None:
            params['tag_id'] = tag_id
        if keyword:
            params['keyword'] = keyword
        return self.client.request('GET', 'email/purchases', params=params)

    def purchase_emails(
        self,
        project_code: str,
        quantity: int,
        email_type: str = "",
        domain: Optional[str] = None
    ) -> Any:
        """
        购买邮箱

        Args:
            project_code: 项目代码
            quantity: 购买数量
            email_type: 邮箱类型
            domain: 指定域名

        Returns:
            购买结果
        """
        data = {
            'project_code': project_code,
            'quantity': quantity,
            'email_type': email_type or "",
            'domain': domain or "",
            'variant_mode': ""
        }

        return self.client.request('POST', 'email/purchase', json=data)

    def get_token_code(self, token: str) -> Any:
        """
        通过 token 获取验证码（已购邮箱）

        Args:
            token: 邮箱 token

        Returns:
            验证码信息，包含 has_new_mail, verification_code, mail 等
            has_new_mail: true=有新邮件, false=暂无新邮件
        """
        return self.client.request('GET', f'email/token/{token}/code')

    def set_purchase_disabled(self, purchase_id: int, disabled: int) -> Any:
        """
        设置已购邮箱禁用状态

        Args:
            purchase_id: 购买记录 ID
            disabled: 禁用状态 (0=启用, 1=禁用)

        Returns:
            设置结果
        """
        data = {'user_disabled': disabled}
        return self.client.request('POST', f'email/{purchase_id}/disable', json=data)

    def create_appeal(
        self,
        appeal_type: int,
        reason: str,
        description: str,
        order_id: Optional[int] = None,
        purchase_id: Optional[int] = None
    ) -> Any:
        """
        创建申诉

        Args:
            appeal_type: 申诉类型 (1=订单, 2=购买)
            reason: 申诉原因
            description: 申诉描述
            order_id: 订单 ID (appeal_type=1 时必填)
            purchase_id: 购买记录 ID (appeal_type=2 时必填)

        Returns:
            申诉结果
        """
        data = {
            'appeal_type': appeal_type,
            'reason': reason,
            'description': description
        }
        if order_id is not None:
            data['order_id'] = order_id
        if purchase_id is not None:
            data['purchase_id'] = purchase_id

        return self.client.request('POST', 'appeal/create', json=data)
