#!/usr/bin/env python3
"""
重新上传账号到 CPA（包含 chatgpt_account_id 字段）
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.core.upload.cpa_upload import upload_to_cpa, generate_token_json


def reupload_accounts(account_ids=None):
    """重新上传指定账号到 CPA"""
    # 初始化数据库
    initialize_database()

    with get_db() as db:
        if account_ids:
            # 上传指定 ID 的账号
            accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
        else:
            # 上传所有有 access_token 的账号
            accounts = db.query(Account).filter(
                Account.access_token.isnot(None),
                Account.access_token != "",
            ).all()

        if not accounts:
            print("❌ 没有找到可上传的账号")
            return

        print(f"找到 {len(accounts)} 个账号需要重新上传")
        print("=" * 60)

        success_count = 0
        failed_count = 0

        for account in accounts:
            print(f"\n上传: {account.email}")

            # 生成新的 token JSON（包含 chatgpt_account_id）
            token_json = generate_token_json(account)

            # 检查是否有 account_id
            if not token_json.get('account_id'):
                print(f"  ⚠️  警告: 缺少 account_id，跳过")
                failed_count += 1
                continue

            # 上传到 CPA
            success, message = upload_to_cpa(token_json)

            if success:
                print(f"  ✅ {message}")
                success_count += 1
            else:
                print(f"  ❌ {message}")
                failed_count += 1

        print("\n" + "=" * 60)
        print(f"上传完成: 成功 {success_count}, 失败 {failed_count}")
        print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="重新上传账号到 CPA")
    parser.add_argument("--ids", type=str, help="账号 ID 列表，用逗号分隔，例如: 1,2,3")
    parser.add_argument("--all", action="store_true", help="上传所有账号")

    args = parser.parse_args()

    if args.ids:
        account_ids = [int(x.strip()) for x in args.ids.split(",")]
        print(f"重新上传账号 ID: {account_ids}")
        reupload_accounts(account_ids)
    elif args.all:
        print("重新上传所有账号")
        reupload_accounts()
    else:
        print("请指定要上传的账号:")
        print("  --ids 1,2,3    上传指定 ID 的账号")
        print("  --all          上传所有账号")
