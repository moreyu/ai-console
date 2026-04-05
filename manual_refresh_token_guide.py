#!/usr/bin/env python3
"""
手动获取 refresh_token 的详细指南和辅助工具
"""

MANUAL_GUIDE = """
================================================================================
手动获取 refresh_token 操作指南
================================================================================

由于 OpenAI 不再在标准 OAuth 流程中返回 refresh_token，需要通过以下方式手动获取：

方法 1: 使用浏览器开发者工具（推荐）
----------------------------------------

1. 打开浏览器（Chrome/Edge）
2. 访问 https://chatgpt.com
3. 使用账号登录（使用 codex-console 注册的账号）
4. 打开开发者工具（F12）
5. 切换到 "Application" 或 "存储" 标签
6. 在左侧找到 "Cookies" -> "https://chatgpt.com"
7. 查找以下 Cookie：
   - __Secure-next-auth.session-token
   - 复制其值，这就是 session_token

8. 切换到 "Network" 或 "网络" 标签
9. 刷新页面（F5）
10. 在请求列表中找到 "session" 请求
11. 点击查看响应内容
12. 查找 "refreshToken" 字段
13. 如果有值，复制它

方法 2: 使用 OAuth 重新授权
----------------------------------------

这个方法可能会获取到 refresh_token，但不保证：

1. 访问以下 URL（替换 YOUR_CLIENT_ID）：

https://auth.openai.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:1455/auth/callback&scope=openid%20email%20profile%20offline_access&state=test&code_challenge=CHALLENGE&code_challenge_method=S256&prompt=login

2. 登录账号
3. 授权后会跳转到回调地址
4. 复制 URL 中的 code 参数
5. 使用 code 交换 token（需要编程）

方法 3: 检查现有的 refresh_token
----------------------------------------

某些情况下，账号可能已经有 refresh_token（例如之前通过其他方式登录过）：

运行以下命令检查：

cd ~/codex-console
python3 << 'EOF'
from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database

initialize_database()

with get_db() as db:
    accounts = db.query(Account).all()

    print("账号 refresh_token 状态:")
    print("=" * 60)

    for acc in accounts:
        has_rt = bool(acc.refresh_token)
        status = "✅ 有" if has_rt else "❌ 无"
        print(f"{acc.id:3d}. {acc.email:40s} {status}")

        if has_rt:
            print(f"     长度: {len(acc.refresh_token)} 字符")
EOF

================================================================================
重要提示
================================================================================

1. OpenAI 可能已经完全移除了 refresh_token 机制
2. 即使获取到 refresh_token，它可能很快就会失效
3. 推荐的长期解决方案是修改 Cliproxy 支持 session_token

================================================================================
"""

print(MANUAL_GUIDE)

# 提供一个交互式工具
def interactive_update():
    """交互式更新 refresh_token"""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))

    from src.database.session import get_db
    from src.database.models import Account
    from src.database.init_db import initialize_database

    initialize_database()

    print("\n交互式 refresh_token 更新工具")
    print("=" * 60)

    # 列出所有账号
    with get_db() as db:
        accounts = db.query(Account).all()

        print("\n可用账号:")
        for acc in accounts:
            rt_status = "有" if acc.refresh_token else "无"
            print(f"  {acc.id}. {acc.email} (refresh_token: {rt_status})")

    print("\n输入账号 ID（输入 q 退出）:")
    account_id = input("> ").strip()

    if account_id.lower() == 'q':
        return

    try:
        account_id = int(account_id)
    except ValueError:
        print("❌ 无效的账号 ID")
        return

    with get_db() as db:
        account = db.query(Account).filter(Account.id == account_id).first()

        if not account:
            print(f"❌ 未找到账号 ID: {account_id}")
            return

        print(f"\n账号: {account.email}")
        print(f"当前 refresh_token: {'有 ({} 字符)'.format(len(account.refresh_token)) if account.refresh_token else '无'}")

        print("\n请输入新的 refresh_token（留空跳过）:")
        new_refresh_token = input("> ").strip()

        if new_refresh_token:
            account.refresh_token = new_refresh_token
            db.commit()
            print(f"✅ 已更新 refresh_token ({len(new_refresh_token)} 字符)")
        else:
            print("⏭️  跳过")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_update()
