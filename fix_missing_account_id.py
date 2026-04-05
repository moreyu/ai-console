#!/usr/bin/env python3
"""
修复缺少 account_id 的账号
从 access_token 的 JWT payload 中提取 account_id
"""

import sys
import json
import base64
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database


def extract_account_id_from_access_token(access_token: str) -> str:
    """从 access_token 的 JWT payload 提取 account_id"""
    try:
        raw = str(access_token or "").strip()
        if raw.count(".") < 2:
            return ""

        payload = raw.split(".")[1]
        pad = "=" * ((4 - (len(payload) % 4)) % 4)
        decoded = base64.urlsafe_b64decode((payload + pad).encode("ascii"))
        claims = json.loads(decoded.decode("utf-8"))

        if not isinstance(claims, dict):
            return ""

        # 尝试从 auth claims 中获取
        auth_claims = claims.get("https://api.openai.com/auth") or {}
        account_id = str(
            auth_claims.get("chatgpt_account_id")
            or claims.get("chatgpt_account_id")
            or ""
        ).strip()

        return account_id
    except Exception as e:
        print(f"提取失败: {e}")
        return ""


def fix_missing_account_ids():
    """修复所有缺少 account_id 的账号"""
    with get_db() as db:
        # 查找所有有 access_token 但缺少 account_id 的账号
        accounts = db.query(Account).filter(
            Account.access_token.isnot(None),
            Account.access_token != "",
        ).all()

        fixed_count = 0
        already_ok_count = 0
        failed_count = 0

        for account in accounts:
            if account.account_id:
                already_ok_count += 1
                continue

            # 尝试从 access_token 提取
            account_id = extract_account_id_from_access_token(account.access_token)

            if account_id:
                account.account_id = account_id
                db.commit()
                print(f"✅ 修复成功: {account.email} -> {account_id}")
                fixed_count += 1
            else:
                print(f"❌ 无法提取: {account.email}")
                failed_count += 1

        print("\n" + "=" * 60)
        print(f"总计: {len(accounts)} 个账号")
        print(f"已有 account_id: {already_ok_count}")
        print(f"成功修复: {fixed_count}")
        print(f"无法修复: {failed_count}")
        print("=" * 60)


if __name__ == "__main__":
    print("开始修复缺少 account_id 的账号...")
    print("=" * 60)

    # 初始化数据库
    initialize_database()

    fix_missing_account_ids()
    print("\n修复完成！")
