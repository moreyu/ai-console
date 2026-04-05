#!/usr/bin/env python3
"""
测试直接上传单个账号到 Cliproxy
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.core.upload.cpa_upload import upload_to_cpa, generate_token_json
from sqlalchemy import text


def test_single_upload(account_id=1):
    """测试上传单个账号"""
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

        # 获取账号
        account = db.query(Account).filter(Account.id == account_id).first()

        if not account:
            print(f"❌ 未找到账号 ID: {account_id}")
            return

        print(f"测试账号: {account.email}")
        print(f"Account ID: {account.account_id}")
        print()

        # 生成 token JSON
        token_json = generate_token_json(account)

        # 显示将要上传的数据（隐藏敏感信息）
        print("上传数据预览:")
        print(f"  type: {token_json['type']}")
        print(f"  email: {token_json['email']}")
        print(f"  account_id: {token_json['account_id']}")
        print(f"  chatgpt_account_id: {token_json['chatgpt_account_id']}")
        print(f"  access_token: {'[有值]' if token_json['access_token'] else '[空]'}")
        print(f"  session_token: {'[有值]' if token_json['session_token'] else '[空]'}")
        print(f"  refresh_token: {'[有值]' if token_json['refresh_token'] else '[空]'}")
        print()

        # 上传
        print("开始上传...")
        success, message = upload_to_cpa(
            token_json,
            api_url=api_url,
            api_token=api_token
        )

        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")


if __name__ == "__main__":
    account_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    test_single_upload(account_id)
