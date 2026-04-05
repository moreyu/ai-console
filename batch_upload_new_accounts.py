#!/usr/bin/env python3
"""
批量上传新注册的账号到 Cliproxy
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.core.upload.cpa_upload import upload_to_cpa, generate_token_json
from sqlalchemy import text


def batch_upload_new_accounts(start_id=7):
    """批量上传新账号"""
    initialize_database()

    # 获取 CPA 服务配置
    with get_db() as db:
        result = db.execute(
            text("SELECT api_url, api_token FROM cpa_services WHERE id = :id"),
            {"id": 1}
        ).fetchone()

        if not result:
            print("❌ 未找到 CPA 服务配置")
            return

        api_url = result[0]
        api_token = result[1]

        print(f"CPA 服务 URL: {api_url}")
        print("=" * 60)

        # 获取所有 ID >= start_id 的账号
        accounts = db.query(Account).filter(Account.id >= start_id).order_by(Account.id).all()

        if not accounts:
            print(f"❌ 没有找到 ID >= {start_id} 的账号")
            return

        print(f"找到 {len(accounts)} 个新账号，开始上传...")
        print()

        success_count = 0
        failed_count = 0

        for account in accounts:
            print(f"上传 ID {account.id}: {account.email}")

            # 生成 token JSON
            token_json = generate_token_json(account)

            # 检查是否有 account_id
            if not token_json.get('account_id'):
                print(f"  ⚠️  警告: 缺少 account_id，跳过")
                failed_count += 1
                continue

            # 上传到 CPA
            success, message = upload_to_cpa(
                token_json,
                api_url=api_url,
                api_token=api_token
            )

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
    batch_upload_new_accounts()
