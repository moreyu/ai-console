# 修复 codex-console 注册流程以获取 refresh_token

## 问题分析

当前注册流程使用"会话复用"（session reuse）方式，直接从 `/api/auth/session` 获取 `access_token`，跳过了标准的 OAuth token 交换流程，导致无法获取 `refresh_token`。

**代码位置：** `src/core/anyauto/register_flow.py` 第 292-314 行

**当前逻辑：**
```python
session_ok, session_result = chatgpt_client.reuse_session_and_get_tokens()
if session_ok and session_result.get("access_token"):
    # 直接返回，只有 access_token 和 session_token
    return {
        "success": True,
        "access_token": session_result.get("access_token", ""),
        "session_token": session_result.get("session_token", ""),
        # ❌ 没有 refresh_token
    }
```

## 解决方案 1：强制使用 OAuth 流程（推荐）

修改注册流程，跳过会话复用，直接使用 OAuth 登录流程。

### 修改文件：`src/core/anyauto/register_flow.py`

在第 290 行左右，找到：
```python
session_ok, session_result = chatgpt_client.reuse_session_and_get_tokens()
if session_ok and session_result.get("access_token"):
```

**修改为：**
```python
# 强制使用 OAuth 流程以获取 refresh_token
session_ok = False  # 跳过会话复用
session_result = {}

# 或者注释掉会话复用部分：
# session_ok, session_result = chatgpt_client.reuse_session_and_get_tokens()
# if session_ok and session_result.get("access_token"):
#     ...原有代码...
```

这样会强制进入第 316 行的 OAuth 回退流程，该流程会调用 `login_and_get_tokens()`，它会执行完整的 OAuth token 交换，**可能**获取到 `refresh_token`。

### 优点
- 简单直接
- 使用标准 OAuth 流程
- 可能获取到 refresh_token

### 缺点
- 注册时间可能稍长
- 如果 OpenAI 确实不再返回 refresh_token，这个方法也无效

## 解决方案 2：会话复用后补充 OAuth 流程

保留会话复用的优势，但在成功后额外执行一次 OAuth 流程尝试获取 `refresh_token`。

### 修改文件：`src/core/anyauto/register_flow.py`

在第 301-314 行的 return 语句之前，添加：

```python
# 尝试通过 OAuth 流程获取 refresh_token
self._log("会话复用成功，尝试补充获取 refresh_token...")
try:
    oauth_client = OAuthClient(
        config=oauth_config,
        proxy=self.proxy_url,
        verbose=False,
        browser_mode=self.browser_mode,
    )
    oauth_client._log = self._log
    oauth_client.session = chatgpt_client.session

    # 尝试 passwordless OAuth 登录
    tokens = oauth_client.login_passwordless_and_get_tokens(
        normalized_email,
        chatgpt_client.device_id,
        chatgpt_client.ua,
        chatgpt_client.sec_ch_ua,
        chatgpt_client.impersonate,
        skymail_adapter,
    )

    if tokens and tokens.get("refresh_token"):
        self._log(f"✅ 成功获取 refresh_token ({len(tokens['refresh_token'])} 字符)")
        # 更新返回值
        return {
            "success": True,
            "access_token": tokens.get("access_token", "") or session_result.get("access_token", ""),
            "refresh_token": tokens.get("refresh_token", ""),
            "id_token": tokens.get("id_token", ""),
            "session_token": session_result.get("session_token", ""),
            "account_id": account_id,
            "workspace_id": workspace_id,
            "metadata": {
                "auth_provider": session_result.get("auth_provider", ""),
                "expires": session_result.get("expires", ""),
                "user_id": session_result.get("user_id", ""),
                "user": session_result.get("user") or {},
                "account": session_result.get("account") or {},
            },
        }
    else:
        self._log("⚠️  OAuth 流程未返回 refresh_token，继续使用会话复用结果")
except Exception as e:
    self._log(f"⚠️  补充 OAuth 流程失败: {e}，继续使用会话复用结果")

# 原有的 return 语句
return {
    "success": True,
    "access_token": session_result.get("access_token", ""),
    "session_token": session_result.get("session_token", ""),
    "account_id": account_id,
    "workspace_id": workspace_id,
    "metadata": {...},
}
```

### 优点
- 保留会话复用的速度优势
- 额外尝试获取 refresh_token
- 即使失败也不影响注册成功

### 缺点
- 增加了一次额外的 OAuth 请求
- 如果 OpenAI 不返回 refresh_token，仍然无效

## 解决方案 3：使用 session_token 作为 refresh_token（临时方案）

如果 OpenAI 确实不再提供 `refresh_token`，我们可以在保存到数据库时，自动将 `session_token` 复制到 `refresh_token` 字段。

### 修改文件：`src/core/register.py`

找到保存账号到数据库的部分（约第 3082 行），在保存前添加：

```python
# 如果没有 refresh_token，使用 session_token 作为替代
if not result.refresh_token and result.session_token:
    result.refresh_token = result.session_token
    logger.info(f"使用 session_token 作为 refresh_token 的替代")
```

### 优点
- 简单快速
- 确保 refresh_token 字段有值
- 不影响注册流程

### 缺点
- session_token 和 refresh_token 格式不同
- Cliproxy 可能无法识别（已验证确实无效）

## 推荐实施顺序

1. **先尝试方案 1**：强制使用 OAuth 流程，看看 OpenAI 是否会返回 `refresh_token`
2. **如果方案 1 无效**：说明 OpenAI 确实不再提供 `refresh_token`
3. **最终方案**：修改 Cliproxy，让它支持使用 `session_token` 刷新 token

## 测试方法

修改后，重新注册一个账号：

```bash
cd ~/codex-console
# 启动服务
python -m src.web.app

# 在 Web UI 中注册一个新账号
# 然后检查数据库
python3 << 'EOF'
from src.database.session import get_db
from src.database.models import Account
from src.database.init_db import initialize_database

initialize_database()

with get_db() as db:
    account = db.query(Account).order_by(Account.id.desc()).first()
    print(f"最新账号: {account.email}")
    print(f"  access_token: {'✅' if account.access_token else '❌'}")
    print(f"  refresh_token: {'✅' if account.refresh_token else '❌'} ({len(account.refresh_token or '')} 字符)")
    print(f"  session_token: {'✅' if account.session_token else '❌'}")
EOF
```

## 相关文件

- `src/core/anyauto/register_flow.py` - 注册流程主逻辑
- `src/core/anyauto/oauth_client.py` - OAuth 客户端
- `src/core/register.py` - 注册引擎
- `CLIPROXY_SESSION_TOKEN_SUPPORT.md` - Cliproxy 修改方案
