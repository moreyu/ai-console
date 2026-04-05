#!/usr/bin/env python3
"""
从浏览器 ChatGPT session 中提取 refresh_token 并更新到数据库
"""

import sys
import json
import base64
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database


def extract_tokens_from_session(session_data):
    """从 /api/auth/session 响应中提取 tokens"""
    try:
        if isinstance(session_data, str):
            session_data = json.loads(session_data)

        access_token = session_data.get('accessToken', '')

        # 尝试从不同位置获取 refresh_token
        refresh_token = (
            session_data.get('refreshToken') or
            session_data.get('refresh_token') or
            ''
        )

        # 从 access_token 中提取 email 和 account_id
        email = ''
        account_id = ''

        if access_token and access_token.count('.') >= 2:
            payload = access_token.split('.')[1]
            pad = '=' * ((4 - (len(payload) % 4)) % 4)
            decoded = base64.urlsafe_b64decode((payload + pad).encode('ascii'))
            claims = json.loads(decoded.decode('utf-8'))

            profile = claims.get('https://api.openai.com/profile', {})
            email = profile.get('email', '')

            auth_claims = claims.get('https://api.openai.com/auth', {})
            account_id = auth_claims.get('chatgpt_account_id', '')

        return {
            'email': email,
            'account_id': account_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    except Exception as e:
        print(f"解析失败: {e}")
        return None


def update_account_tokens(email, tokens):
    """更新账号的 tokens"""
    initialize_database()

    with get_db() as db:
        account = db.query(Account).filter(Account.email == email).first()

        if not account:
            print(f"❌ 未找到账号: {email}")
            return False

        # 更新 tokens
        if tokens.get('access_token'):
            account.access_token = tokens['access_token']

        if tokens.get('refresh_token'):
            account.refresh_token = tokens['refresh_token']
            print(f"✅ 已更新 refresh_token")
        else:
            print(f"⚠️  警告: session 中没有 refresh_token")

        if tokens.get('account_id') and not account.account_id:
            account.account_id = tokens['account_id']
            print(f"✅ 已更新 account_id: {tokens['account_id']}")

        db.commit()
        return True


def main():
    print("=" * 60)
    print("从浏览器 ChatGPT Session 提取并更新 Tokens")
    print("=" * 60)
    print()
    print("步骤:")
    print("1. 在浏览器中登录 ChatGPT")
    print("2. 打开开发者工具 (F12)")
    print("3. 访问: https://chatgpt.com/api/auth/session")
    print("4. 复制整个 JSON 响应")
    print("5. 粘贴到下面 (输入 END 结束):")
    print()

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break

    session_json = '\n'.join(lines)

    if not session_json.strip():
        print("❌ 未输入任何内容")
        return

    print("\n解析 session 数据...")
    tokens = extract_tokens_from_session(session_json)

    if not tokens:
        print("❌ 解析失败")
        return

    print(f"\n提取的信息:")
    print(f"  Email: {tokens['email']}")
    print(f"  Account ID: {tokens['account_id']}")
    print(f"  Access Token: {'有' if tokens['access_token'] else '无'} ({len(tokens['access_token'])} 字符)")
    print(f"  Refresh Token: {'有' if tokens['refresh_token'] else '无'} ({len(tokens['refresh_token'])} 字符)")

    if not tokens['email']:
        print("\n❌ 无法提取 email，请检查 session 数据是否正确")
        return

    print(f"\n更新账号: {tokens['email']}")
    if update_account_tokens(tokens['email'], tokens):
        print("\n✅ 更新成功！")
        print("\n现在可以重新上传到 Cliproxy 了")
    else:
        print("\n❌ 更新失败")


if __name__ == "__main__":
    main()
