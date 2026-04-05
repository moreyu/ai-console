#!/usr/bin/env python3
"""
导出账号为 CPA JSON 文件
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


def export_accounts_to_json(account_ids, output_dir="./cpa_exports"):
    """导出账号为 JSON 文件"""
    # 初始化数据库
    initialize_database()

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    with get_db() as db:
        accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()

        if not accounts:
            print("❌ 没有找到指定的账号")
            return

        print(f"导出 {len(accounts)} 个账号到 {output_path}")
        print("=" * 60)

        for account in accounts:
            # 生成 token JSON（包含 chatgpt_account_id）
            token_json = generate_token_json(account)

            # 保存为文件
            filename = f"{account.email}.json"
            file_path = output_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(token_json, f, ensure_ascii=False, indent=2)

            print(f"✅ {account.email}")
            print(f"   文件: {file_path}")
            print(f"   account_id: {token_json.get('account_id')}")
            print(f"   chatgpt_account_id: {token_json.get('chatgpt_account_id')}")
            print()

        print("=" * 60)
        print(f"所有文件已导出到: {output_path.absolute()}")
        print("\n你可以手动上传这些 JSON 文件到 Cliproxy")


if __name__ == "__main__":
    # 导出最近的 3 个账号
    account_ids = [1, 2, 3]
    export_accounts_to_json(account_ids)
