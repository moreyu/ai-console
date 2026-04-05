#!/usr/bin/env python3
"""
使用数据库中的 CPA 服务配置重新上传账号
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
from sqlalchemy import text


def get_cpa_service_config(service_id=1):
    """从数据库获取 CPA 服务配置"""
    with get_db() as db:
        result = db.execute(
            text("SELECT api_url, api_token FROM cpa_services WHERE id = :id"),
            {"id": service_id}
        ).fetchone()

        if result:
            return {
                'api_url': result[0],
                'api_token': result[1]
            }
        return None


def reupload_accounts_with_config(account_ids):
    """使用数据库配置重新上传账号"""
    # 初始化数据库
    initialize_database()

    # 获取 CPA 服务配置
    config = get_cpa_service_config(service_id=1)

    if not config:
        print("❌ 未找到 CPA 服务配置")
        return

    print(f"CPA 服务 URL: {config['api_url']}")
    print(f"重新上传账号 ID: {account_ids}")
    print("=" * 60)

    with get_db() as db:
        accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()

        if not accounts:
            print("❌ 没有找到指定的账号")
            return

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

            # 上传到 CPA（使用数据库中的配置）
            success, message = upload_to_cpa(
                token_json,
                api_url=config['api_url'],
                api_token=config['api_token']
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
    # 重新上传最近的 3 个账号
    account_ids = [1, 2, 3]
    reupload_accounts_with_config(account_ids)
