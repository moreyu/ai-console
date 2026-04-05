#!/usr/bin/env python3
"""
生成多种可能的 CPA 格式进行测试
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database

initialize_database()

output_dir = Path.home() / 'Downloads' / 'cpa_test_formats'
output_dir.mkdir(exist_ok=True)

with get_db() as db:
    # 获取一个测试账号
    account = db.query(Account).filter(Account.id == 6).first()

    if not account:
        print("未找到测试账号")
        sys.exit(1)

    account_id = account.account_id
    email = account.email

    # 格式 1: 当前格式（顶层 chatgpt_account_id）
    format1 = {
        "type": "codex",
        "email": email,
        "account_id": account_id,
        "chatgpt_account_id": account_id,
        "access_token": account.access_token,
        "refresh_token": account.refresh_token or "",
        "id_token": account.id_token or "",
        "expired": "",
        "last_refresh": ""
    }

    # 格式 2: 只有 account_id，没有 chatgpt_account_id
    format2 = {
        "type": "codex",
        "email": email,
        "account_id": account_id,
        "access_token": account.access_token,
        "refresh_token": account.refresh_token or "",
        "id_token": account.id_token or "",
        "expired": "",
        "last_refresh": ""
    }

    # 格式 3: 嵌套的 account 对象
    format3 = {
        "type": "codex",
        "email": email,
        "account": {
            "id": account_id,
            "chatgpt_account_id": account_id
        },
        "access_token": account.access_token,
        "refresh_token": account.refresh_token or "",
        "id_token": account.id_token or "",
        "expired": "",
        "last_refresh": ""
    }

    # 格式 4: 使用 user_id 而不是 account_id
    format4 = {
        "type": "codex",
        "email": email,
        "user_id": account_id,
        "chatgpt_account_id": account_id,
        "access_token": account.access_token,
        "refresh_token": account.refresh_token or "",
        "id_token": account.id_token or "",
        "expired": "",
        "last_refresh": ""
    }

    # 格式 5: 所有可能的 ID 字段都加上
    format5 = {
        "type": "codex",
        "email": email,
        "account_id": account_id,
        "chatgpt_account_id": account_id,
        "user_id": account_id,
        "id": account_id,
        "access_token": account.access_token,
        "refresh_token": account.refresh_token or "",
        "id_token": account.id_token or "",
        "expired": "",
        "last_refresh": ""
    }

    formats = {
        "format1_current": format1,
        "format2_account_id_only": format2,
        "format3_nested": format3,
        "format4_user_id": format4,
        "format5_all_ids": format5
    }

    print(f"生成 {len(formats)} 种测试格式:")
    print("=" * 60)

    for name, fmt in formats.items():
        filename = f"{name}_{email}.json"
        file_path = output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fmt, f, ensure_ascii=False, indent=2)

        print(f"✅ {name}")
        print(f"   文件: {filename}")

        # 显示 ID 相关字段
        id_fields = {k: v for k, v in fmt.items() if 'id' in k.lower() and k != 'id_token'}
        print(f"   ID 字段: {json.dumps(id_fields, indent=6)}")
        print()

    print("=" * 60)
    print(f"测试文件已生成到: {output_dir}")
    print("\n请依次上传这些文件到 Cliproxy 测试哪种格式能工作")
    print("文件名说明:")
    print("  format1: 当前格式（account_id + chatgpt_account_id）")
    print("  format2: 只有 account_id")
    print("  format3: 嵌套的 account 对象")
    print("  format4: 使用 user_id")
    print("  format5: 包含所有可能的 ID 字段")
