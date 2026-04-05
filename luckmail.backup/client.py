"""
LuckMail API Client
"""

import requests
from typing import Any, Dict, Optional
from .user import UserAPI


class LuckMailClient:
    """LuckMail API 客户端"""

    def __init__(self, base_url: str, api_key: str):
        """
        初始化客户端

        Args:
            base_url: API 基础地址
            api_key: API 密钥
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LuckMail-Python-SDK/0.1.0'
        })

        # 初始化子模块
        self.user = UserAPI(self)

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: 其他请求参数

        Returns:
            响应数据
        """
        # 确保端点以 /api/v1/openapi/ 开头
        if not endpoint.startswith('/api/v1/openapi/'):
            endpoint = f"/api/v1/openapi/{endpoint.lstrip('/')}"

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            # 尝试解析 JSON
            try:
                data = response.json()
                return self._parse_response(data)
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {e}")

    def _parse_response(self, data: Any) -> Any:
        """
        解析 API 响应

        Args:
            data: 响应数据

        Returns:
            解析后的数据
        """
        # 如果是字典且包含 code 字段，检查是否成功
        if isinstance(data, dict):
            code = data.get('code', 0)
            if code != 0 and code != 200:
                msg = data.get('message', data.get('msg', 'Unknown error'))
                raise Exception(f"API 返回错误: {msg} (code: {code})")

            # 返回 data 字段或整个响应
            if 'data' in data:
                return self._wrap_response(data['data'])
            return self._wrap_response(data)

        return self._wrap_response(data)

    def _wrap_response(self, data: Any) -> Any:
        """
        包装响应数据，使其支持属性访问

        Args:
            data: 原始数据

        Returns:
            包装后的数据
        """
        if isinstance(data, dict):
            return ResponseWrapper(data)
        elif isinstance(data, list):
            return [self._wrap_response(item) for item in data]
        return data


class ResponseWrapper:
    """响应数据包装器，支持属性访问"""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self._data.get(name)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __repr__(self) -> str:
        return f"ResponseWrapper({self._data})"

    def __bool__(self) -> bool:
        return bool(self._data)
