#!/usr/bin/env python3
"""
使用 session_token 自动提取 refresh_token 并更新数据库
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.core.openai.token_refresh import TokenRefreshManager
from curl_cffi import requests as cffi_requests
import json


def extract_refresh_token_from_session_token(session_token: str, proxy_url: str = None) -> dict:
    """
    使用 session_token 获取完整的会话信息，包括 refresh_token

    Args:
        session_token: Session Token
        proxy_url: 代理 URL

    Returns:
        包含 access_token 和 refresh_token 的字典
    """
    session_url = "https://chatgpt.com/api/auth/session"

    try:
        # 创建会话
        session = cffi_requests.Session(
            impersonate="chrome120",
            proxy=proxy_url
        )

        # 设置 cookie
        session.cookies.set(
            "__Secure-next-auth.session-token",
            session_token,
            domain=".chatgpt.com",
            path="/"
        )

        # 请求会话信息
        response = session.get(
            session_url,
            headers={
                "accept": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=30
        )

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }

        data = response.json()

        # 提取 tokens
        access_token = data.get("accessToken", "")
        refresh_token = data.get("refreshToken", "")

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "has_refresh_token": bool(refresh_token)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def update_account_refresh_token(account_id: int, proxy_url: str = None) -> bool:
    """
    更新账号的 refresh_token

    Args:
        account_id: 账号 ID
        proxy_url: 代理 URL

    Returns:
        是否成功
    """
    initialize_database()

    with get_db() as db:
        account = db.query(Account).filter(Account.id == account_id).first()

        if not account:
            print(f"❌ 未找到账号 ID: {account_id}")
            return False

        if not account.session_token:
            print(f"❌ 账号 {account.email} 没有 session_token")
            return False

        print(f"处理账号: {account.email}")
        print(f"  使用 session_token 获取 refresh_token...")

        # 提取 refresh_token
        result = extract_refresh_token_from_session_token(
            account.session_token,
            proxy_url=proxy_url
        )

        if not result["success"]:
            print(f"  ❌ 失败: {result.get('error', '未知错误')}")
            return False

        if not result["has_refresh_token"]:
            print(f"  ⚠️  警告: OpenAI 未返回 refresh_token")
            print(f"  这可能是 OpenAI 的限制，session_token 仍然可以用于刷新")
            return False

        # 更新数据库
        account.refresh_token = result["refresh_token"]

        # 同时更新 access_token（如果有新的）
        if result["access_token"]:
            account.access_token = result["access_token"]

        db.commit()

        print(f"  ✅ 成功更新 refresh_token ({len(result['refresh_token'])} 字符)")
        return True


def batch_update_accounts(account_ids: list = None, proxy_url: str = None):
    """
    批量更新账号的 refresh_token

    Args:
        account_ids: 账号 ID 列表，如果为 None 则更新所有缺少 refresh_token 的账号
        proxy_url: 代理 URL
    """
    initialize_database()

    with get_db() as db:
        if account_ids:
            accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
        else:
            # 查找所有有 session_token 但没有 refresh_token 的账号
            accounts = db.query(Account).filter(
                Account.session_token.isnot(None),
                Account.session_token != "",
                (Account.refresh_token.is_(None)) | (Account.refresh_token == "")
            ).all()

        if not accounts:
            print("没有需要更新的账号")
            return

        print(f"找到 {len(accounts)} 个需要更新的账号")
        print("=" * 60)

        success_count = 0
        failed_count = 0

        for account in accounts:
            if update_account_refresh_token(account.id, proxy_url=proxy_url):
                success_count += 1
            else:
                failed_count += 1
            print()

        print("=" * 60)
        print(f"完成: 成功 {success_count}, 失败 {failed_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="从 session_token 提取 refresh_token")
    parser.add_argument("--ids", type=str, help="账号 ID 列表，用逗号分隔，如: 1,2,3")
    parser.add_argument("--all", action="store_true", help="更新所有缺少 refresh_token 的账号")
    parser.add_argument("--proxy", type=str, help="代理 URL")

    args = parser.parse_args()

    if args.ids:
        account_ids = [int(x.strip()) for x in args.ids.split(",")]
        batch_update_accounts(account_ids=account_ids, proxy_url=args.proxy)
    elif args.all:
        batch_update_accounts(proxy_url=args.proxy)
    else:
        # 默认更新 ID 1, 2, 3
        print("未指定账号 ID，默认更新账号 1, 2, 3")
        print("使用 --ids 1,2,3 指定账号，或使用 --all 更新所有账号")
        print()
        batch_update_accounts(account_ids=[1, 2, 3], proxy_url=args.proxy)
