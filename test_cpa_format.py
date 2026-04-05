#!/usr/bin/env python3
"""
测试 CPA 上传格式
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.core.upload.cpa_upload import generate_token_json


def test_cpa_format():
    """测试 CPA 上传格式"""
    # 初始化数据库
    initialize_database()

    with get_db() as db:
        # 获取一个有 access_token 的账号
        account = db.query(Account).filter(
            Account.access_token.isnot(None),
            Account.access_token != "",
        ).first()

        if not account:
            print("❌ 没有找到可用的账号")
            return

        print(f"测试账号: {account.email}")
        print("=" * 60)

        # 生成 CPA 格式的 JSON
        token_json = generate_token_json(account)

        print("\n生成的 CPA JSON:")
        print(json.dumps(token_json, ensure_ascii=False, indent=2))

        print("\n" + "=" * 60)
        print("字段检查:")
        print(f"✓ type: {token_json.get('type')}")
        print(f"✓ email: {token_json.get('email')}")
        print(f"✓ account_id: {token_json.get('account_id')} {'✅' if token_json.get('account_id') else '❌ 缺失'}")
        print(f"✓ access_token: {'有' if token_json.get('access_token') else '无'} ({len(token_json.get('access_token', ''))} 字符)")
        print(f"✓ refresh_token: {'有' if token_json.get('refresh_token') else '无'} ({len(token_json.get('refresh_token', ''))} 字符)")
        print(f"✓ id_token: {'有' if token_json.get('id_token') else '无'} ({len(token_json.get('id_token', ''))} 字符)")
        print(f"✓ expired: {token_json.get('expired')}")
        print(f"✓ last_refresh: {token_json.get('last_refresh')}")

        # 检查必需字段
        required_fields = ['type', 'email', 'account_id', 'access_token']
        missing_fields = [f for f in required_fields if not token_json.get(f)]

        if missing_fields:
            print(f"\n❌ 缺少必需字段: {', '.join(missing_fields)}")
        else:
            print("\n✅ 所有必需字段都存在")


if __name__ == "__main__":
    test_cpa_format()
