#!/usr/bin/env python3
"""
简单的批量注册脚本
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.init_db import initialize_database
from src.core.anyauto.register_flow import AnyAutoRegistrationEngine
from src.services.luckmail import LuckMailService

async def register_one():
    """注册一个账号"""
    try:
        # 创建邮箱服务
        email_service = LuckMailService()

        # 创建注册引擎
        engine = AnyAutoRegistrationEngine(
            email_service=email_service,
            proxy_url=None,
            max_retries=3
        )

        # 执行注册
        result = engine.run()

        if result and result.get("success"):
            print(f"✅ 成功: {result.get('email', 'Unknown')}")
            return True
        else:
            error = result.get("error_message", "Unknown error") if result else "No result"
            print(f"❌ 失败: {error}")
            return False

    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

async def main():
    initialize_database()

    count = 10
    print(f"开始批量注册 {count} 个账号...")
    print("=" * 60)

    success = 0
    failed = 0

    for i in range(count):
        print(f"\n[{i+1}/{count}] 注册账号...")
        if await register_one():
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"完成: 成功 {success}, 失败 {failed}")

if __name__ == "__main__":
    asyncio.run(main())
