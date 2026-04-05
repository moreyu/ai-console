#!/usr/bin/env python3
"""
Team 邀请脚本
使用 codex-console 的 Team 账号邀请免费账号
"""

import sys
import os
import json
import base64

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.session import init_database, get_db
from src.database.models import Account
from curl_cffi import requests as cffi_requests

def send_team_invite(access_token: str, workspace_id: str, target_email: str):
    """发送 Team 邀请"""
    url = f"https://chatgpt.com/backend-api/accounts/{workspace_id}/invites"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/",
        "chatgpt-account-id": workspace_id,
    }
    payload = {
        "email_addresses": [target_email],
        "role": "standard-user",
        "resend_emails": True,
    }

    try:
        response = cffi_requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
            impersonate="chrome110",
        )
        return response.status_code, response.text
    except Exception as e:
        return 599, str(e)

def get_workspace_id_from_token(access_token: str) -> str:
    """从 access_token 中提取 workspace_id"""
    try:
        parts = access_token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            padding = '=' * ((4 - len(payload) % 4) % 4)
            decoded = base64.urlsafe_b64decode(payload + padding)
            claims = json.loads(decoded)
            auth_info = claims.get('https://api.openai.com/auth', {})
            return auth_info.get('chatgpt_account_id', '')
    except Exception as e:
        print(f"解析 token 失败: {e}")
    return ''

def main():
    init_database()

    # Team 账号 ID
    team_account_id = 7

    # 要邀请的免费账号 ID
    free_account_ids = [1, 2, 3, 5, 6]

    with get_db() as db:
        # 获取 Team 账号
        team_account = db.query(Account).filter(Account.id == team_account_id).first()
        if not team_account:
            print(f"错误: 找不到 Team 账号 (ID: {team_account_id})")
            return

        if not team_account.access_token:
            print("错误: Team 账号缺少 access_token")
            return

        # 获取 workspace_id
        workspace_id = get_workspace_id_from_token(team_account.access_token)
        if not workspace_id:
            print("错误: 无法从 access_token 中提取 workspace_id")
            return

        print(f"Team 账号: {team_account.email}")
        print(f"Workspace ID: {workspace_id}")
        print(f"开始邀请 {len(free_account_ids)} 个免费账号...\n")

        success_count = 0
        failed_count = 0

        for account_id in free_account_ids:
            # 获取免费账号
            free_account = db.query(Account).filter(Account.id == account_id).first()
            if not free_account:
                print(f"✗ ID {account_id}: 账号不存在")
                failed_count += 1
                continue

            print(f"正在邀请: {free_account.email} (ID: {account_id})")

            try:
                status_code, response_text = send_team_invite(
                    access_token=team_account.access_token,
                    workspace_id=workspace_id,
                    target_email=free_account.email
                )

                if 200 <= status_code < 300:
                    print(f"✓ {free_account.email}: 邀请成功")
                    success_count += 1
                elif status_code in (409, 422):
                    print(f"✓ {free_account.email}: 已在 Team 内或已存在邀请")
                    success_count += 1
                else:
                    print(f"✗ {free_account.email}: HTTP {status_code} - {response_text[:100]}")
                    failed_count += 1

            except Exception as e:
                print(f"✗ {free_account.email}: 异常 - {str(e)}")
                failed_count += 1

        print(f"\n邀请完成!")
        print(f"成功: {success_count}")
        print(f"失败: {failed_count}")

if __name__ == "__main__":
    main()
