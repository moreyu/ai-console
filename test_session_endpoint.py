#!/usr/bin/env python3
"""
测试 ChatGPT session endpoint 返回什么数据
需要手动提供一个有效的 session token
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("测试 ChatGPT /api/auth/session 响应")
print("=" * 60)
print()
print("请提供一个有效的 __Secure-next-auth.session-token cookie 值:")
print("(从浏览器开发者工具中复制)")
print()

session_token = input("Session Token: ").strip()

if not session_token:
    print("❌ 未输入 session token")
    sys.exit(1)

print("\n正在请求 /api/auth/session...")

try:
    from curl_cffi import requests as cffi_requests

    session = cffi_requests.Session()

    # 设置 cookie
    session.cookies.set(
        "__Secure-next-auth.session-token",
        session_token,
        domain=".chatgpt.com",
        path="/"
    )

    # 请求 session endpoint
    response = session.get(
        "https://chatgpt.com/api/auth/session",
        headers={
            "accept": "application/json",
            "referer": "https://chatgpt.com/",
        },
        timeout=30,
        impersonate="chrome110"
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        print("\n✅ 成功获取 session 数据")
        print("\n响应中的所有字段:")
        print(json.dumps(list(data.keys()), indent=2))

        print("\n详细数据:")
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: <长度 {len(value)} 字符>")
            elif isinstance(value, dict):
                print(f"  {key}: {json.dumps(value, indent=4)}")
            else:
                print(f"  {key}: {value}")

        # 检查是否有 refresh_token
        print("\n" + "=" * 60)
        if "refreshToken" in data or "refresh_token" in data:
            print("✅ 找到 refresh_token!")
            refresh_token = data.get("refreshToken") or data.get("refresh_token")
            print(f"   长度: {len(refresh_token)} 字符")
        else:
            print("❌ 响应中没有 refresh_token 字段")
            print("\n可能的原因:")
            print("1. refresh_token 存储在 httpOnly cookie 中")
            print("2. ChatGPT 不再使用 refresh_token")
            print("3. 需要通过其他 API 获取")

        # 检查 cookies
        print("\n响应中的 Cookies:")
        for cookie in session.cookies:
            if 'token' in cookie.name.lower() or 'refresh' in cookie.name.lower():
                print(f"  {cookie.name}: {cookie.value[:50]}...")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
