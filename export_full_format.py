#!/usr/bin/env python3
"""
生成完整格式的 CPA JSON 文件（包含所有可能的字段）
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


def generate_full_token_json(account: Account) -> dict:
    """生成包含所有字段的完整 CPA JSON"""
    account_id_value = account.account_id or ""

    # 基础字段
    token_json = {
        "type": "codex",
        "email": account.email,
        "expired": account.expires_at.strftime("%Y-%m-%dT%H:%M:%S+08:00") if account.expires_at else "",
        "id_token": account.id_token or "",
        "account_id": account_id_value,
        "chatgpt_account_id": account_id_value,  # Cliproxy 需要
        "access_token": account.access_token or "",
        "last_refresh": account.last_refresh.strftime("%Y-%m-%dT%H:%M:%S+08:00") if account.last_refresh else "",
        "refresh_token": account.refresh_token or "",
    }

    # 如果没有 account_id，尝试从 access_token 提取
    if not account_id_value and account.access_token:
        import base64
        try:
            payload = account.access_token.split('.')[1]
            pad = '=' * ((4 - (len(payload) % 4)) % 4)
            decoded = base64.urlsafe_b64decode((payload + pad).encode('ascii'))
            claims = json.loads(decoded.decode('utf-8'))
            auth_claims = claims.get('https://api.openai.com/auth', {})
            extracted_id = auth_claims.get('chatgpt_account_id', '')
            if extracted_id:
                token_json['account_id'] = extracted_id
                token_json['chatgpt_account_id'] = extracted_id
        except Exception:
            pass

    return token_json


def export_full_format(account_ids, output_dir="./cpa_exports_full"):
    """导出完整格式的 JSON 文件"""
    # 初始化数据库
    initialize_database()

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    with get_db() as db:
        accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()

        if not accounts:
            print("❌ 没有找到指定的账号")
            return

        print(f"导出 {len(accounts)} 个账号（完整格式）到 {output_path}")
        print("=" * 60)

        for account in accounts:
            # 生成完整格式的 token JSON
            token_json = generate_full_token_json(account)

            # 保存为文件
            filename = f"{account.email}.json"
            file_path = output_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(token_json, f, ensure_ascii=False, indent=2)

            print(f"✅ {account.email}")
            print(f"   文件: {file_path}")
            print(f"   account_id: {token_json.get('account_id')}")
            print(f"   chatgpt_account_id: {token_json.get('chatgpt_account_id')}")

            # 验证两个字段是否一致
            if token_json.get('account_id') != token_json.get('chatgpt_account_id'):
                print(f"   ⚠️  警告: account_id 和 chatgpt_account_id 不一致！")

            print()

        print("=" * 60)
        print(f"所有文件已导出到: {output_path.absolute()}")


if __name__ == "__main__":
    # 导出最近的 3 个账号
    account_ids = [1, 2, 3]
    export_full_format(account_ids)

    # 同时复制到 Downloads
    import shutil
    src_dir = Path("./cpa_exports_full")
    dst_dir = Path.home() / "Downloads"

    print("\n复制到 Downloads 文件夹...")
    for json_file in src_dir.glob("*.json"):
        dst_file = dst_dir / json_file.name
        shutil.copy2(json_file, dst_file)
        print(f"✅ {json_file.name}")

    print("\n完成！文件已更新到 Downloads 文件夹")
