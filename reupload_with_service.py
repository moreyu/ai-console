#!/usr/bin/env python3
"""
使用配置的 CPA 服务重新上传账号
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.core.upload.cpa_upload import batch_upload_to_cpa


def reupload_with_service(account_ids, service_id=1):
    """使用指定的 CPA 服务重新上传账号"""
    # 初始化数据库
    initialize_database()

    print(f"使用 CPA 服务 ID: {service_id}")
    print(f"重新上传账号 ID: {account_ids}")
    print("=" * 60)

    # 使用 batch_upload_to_cpa，它会自动从 cpa_services 表读取配置
    result = batch_upload_to_cpa(
        account_ids=account_ids,
        proxy=None,
        api_url=None,  # 会从 service_id 读取
        api_token=None,  # 会从 service_id 读取
    )

    print("\n上传结果:")
    print("=" * 60)
    print(f"成功: {result.get('success', 0)}")
    print(f"失败: {result.get('failed', 0)}")

    if result.get('details'):
        print("\n详细信息:")
        for detail in result['details']:
            status = "✅" if detail.get('success') else "❌"
            print(f"{status} {detail.get('email')}: {detail.get('message')}")


if __name__ == "__main__":
    # 重新上传最近的 3 个账号
    account_ids = [1, 2, 3]
    reupload_with_service(account_ids, service_id=1)
