#!/usr/bin/env python3
"""批量重新登录账户"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database
from src.services.email_service_factory import EmailServiceFactory
from src.core.anyauto.register_flow import AnyAutoRegistrationEngine

async def relogin_account(account_id: int):
    """重新登录单个账户"""
    initialize_database()
    
    with get_db() as db:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            print(f"❌ 账户 ID {account_id} 不存在")
            return False
        
        print(f"\n{'='*60}")
        print(f"重新登录: {account.email}")
        print(f"{'='*60}")
        
        try:
            # 创建邮箱服务
            email_service = EmailServiceFactory.create_from_env()
            
            # 创建注册引擎
            engine = AnyAutoRegistrationEngine(
                email_service=email_service,
                callback_logger=lambda msg: print(f"  {msg}")
            )
            
            # 重新登录
            result = await engine.relogin_existing_account(
                email=account.email,
                password=account.password
            )
            
            if result.get('success'):
                print(f"✅ {account.email} 登录成功")
                return True
            else:
                print(f"❌ {account.email} 登录失败: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ {account.email} 登录异常: {str(e)}")
            return False

async def batch_relogin(account_ids):
    """批量重新登录"""
    results = []
    for account_id in account_ids:
        success = await relogin_account(account_id)
        results.append((account_id, success))
        await asyncio.sleep(2)  # 避免请求过快
    
    print(f"\n{'='*60}")
    print("登录结果汇总:")
    success_count = sum(1 for _, success in results if success)
    print(f"成功: {success_count}/{len(results)}")
    for account_id, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} 账户 ID {account_id}")

if __name__ == "__main__":
    account_ids = [1, 2, 3, 5, 6]
    asyncio.run(batch_relogin(account_ids))
