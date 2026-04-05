#!/usr/bin/env python3
"""导出账户时自动生成 id_token"""
import sys
import json
import base64
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database

def create_id_token_from_access_token(access_token):
    """从 access_token 中提取信息并构造 id_token"""
    if not access_token:
        return None
    
    try:
        parts = access_token.split('.')
        if len(parts) != 3:
            return None
            
        payload = parts[1]
        padding = '=' * ((4 - len(payload) % 4) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        claims = json.loads(decoded)
        
        auth_info = claims.get('https://api.openai.com/auth', {})
        
        id_token_payload = {
            "email": claims.get('https://api.openai.com/profile', {}).get('email', ''),
            "https://api.openai.com/auth": auth_info,
            "exp": claims.get('exp'),
            "iat": claims.get('iat'),
            "iss": claims.get('iss', 'https://auth.openai.com'),
            "sub": claims.get('sub', '')
        }
        
        header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip('=')
        payload_encoded = base64.urlsafe_b64encode(json.dumps(id_token_payload).encode()).decode().rstrip('=')
        
        return f"{header}.{payload_encoded}."
    except Exception as e:
        print(f"生成 id_token 失败: {e}")
        return None

def export_accounts_with_id_token(account_ids=None):
    """导出账户，自动生成 id_token"""
    initialize_database()
    
    output_path = Path('./cpa_exports_full')
    output_path.mkdir(exist_ok=True)
    
    with get_db() as db:
        if account_ids:
            accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
        else:
            accounts = db.query(Account).all()
        
        print(f"导出 {len(accounts)} 个账户")
        print("="*60)
        
        for account in accounts:
            # 如果没有 id_token，尝试生成
            id_token = account.id_token
            if not id_token and account.access_token:
                id_token = create_id_token_from_access_token(account.access_token)
                if id_token:
                    # 更新数据库
                    account.id_token = id_token
                    db.commit()
                    print(f"  为 {account.email} 生成了 id_token")
            
            token_json = {
                'type': 'codex',
                'email': account.email,
                'expired': account.expires_at.strftime('%Y-%m-%dT%H:%M:%S+08:00') if account.expires_at else '',
                'id_token': id_token or '',
                'account_id': account.account_id or '',
                'chatgpt_account_id': account.account_id or '',
                'access_token': account.access_token or '',
                'last_refresh': account.last_refresh.strftime('%Y-%m-%dT%H:%M:%S+08:00') if account.last_refresh else '',
                'refresh_token': account.refresh_token or '',
                'session_token': account.session_token or '',
                'disabled': False
            }
            
            filename = f'{account.email}.json'
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(token_json, f, ensure_ascii=False, indent=2)
            
            print(f'✅ {account.email}')

        print("="*60)
        print(f"所有文件已导出到: {output_path.absolute()}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="导出账户（自动生成 id_token）")
    parser.add_argument("--ids", type=str, help="账号 ID 列表，用逗号分隔")
    parser.add_argument("--all", action="store_true", help="导出所有账号")
    
    args = parser.parse_args()
    
    if args.ids:
        account_ids = [int(x.strip()) for x in args.ids.split(",")]
        export_accounts_with_id_token(account_ids)
    elif args.all:
        export_accounts_with_id_token()
    else:
        print("请使用 --ids 或 --all 参数")
        print("示例: python export_with_id_token.py --all")
        print("示例: python export_with_id_token.py --ids 1,2,3")
