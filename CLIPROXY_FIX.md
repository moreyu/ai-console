# Cliproxy Account ID 问题修复

## 问题描述

从 codex-console 注册的 GPT 账号上传到 Cliproxy 后，查看 codex 配额显示：
```
额度获取失败：Codex 凭证缺少 ChatGPT 账号 ID
```

## 根本原因

Cliproxy 期望的字段名是 `chatgpt_account_id`，而 codex-console 只提供了 `account_id` 字段。

## 解决方案

### 1. 修改 CPA 上传格式

在 `src/core/upload/cpa_upload.py` 的 `generate_token_json` 函数中添加了 `chatgpt_account_id` 字段：

```python
def generate_token_json(account: Account) -> dict:
    account_id_value = account.account_id or ""
    return {
        "type": "codex",
        "email": account.email,
        "expired": account.expires_at.strftime("%Y-%m-%dT%H:%M:%S+08:00") if account.expires_at else "",
        "id_token": account.id_token or "",
        "account_id": account_id_value,
        "chatgpt_account_id": account_id_value,  # 兼容 Cliproxy
        "access_token": account.access_token or "",
        "last_refresh": account.last_refresh.strftime("%Y-%m-%dT%H:%M:%S+08:00") if account.last_refresh else "",
        "refresh_token": account.refresh_token or "",
    }
```

### 2. 验证修复

运行测试脚本验证：
```bash
cd ~/codex-console
python test_cpa_format.py
```

输出示例：
```json
{
  "type": "codex",
  "email": "example@outlook.com",
  "account_id": "75987746-6a22-4674-b853-8a8983d13921",
  "chatgpt_account_id": "75987746-6a22-4674-b853-8a8983d13921",
  "access_token": "eyJhbGci...",
  ...
}
```

## 使用方法

### 重新上传现有账号

1. 登录 codex-console Web UI: http://localhost:8000
2. 进入账号管理页面
3. 选择要上传的账号
4. 点击"上传到 CPA"
5. 新上传的账号将包含 `chatgpt_account_id` 字段

### 自动上传新注册的账号

在注册设置中启用"自动上传到 CPA"，新注册的账号会自动包含正确的字段。

## 验证

上传后在 Cliproxy 中检查：
1. 进入 Cliproxy 管理界面
2. 查看账号详情
3. 检查 codex 配额是否正常显示

## 注意事项

1. **已上传的旧账号**：需要重新上传才能包含 `chatgpt_account_id` 字段
2. **兼容性**：同时保留了 `account_id` 和 `chatgpt_account_id` 两个字段，确保向后兼容
3. **account_id 来源**：从 access_token 的 JWT payload 中自动提取

## 故障排查

### 问题：上传后仍然提示缺少 account_id

**检查步骤：**

1. 验证账号是否有 account_id：
```bash
cd ~/codex-console
sqlite3 data/database.db "SELECT email, account_id FROM accounts WHERE email='your@email.com';"
```

2. 如果 account_id 为空，运行修复脚本：
```bash
python fix_missing_account_id.py
```

3. 重新上传账号

### 问题：access_token 无法提取 account_id

**原因：** access_token 可能已过期或格式不正确

**解决方案：**
1. 在 codex-console 中刷新账号 token
2. 或者重新注册账号

## 相关文件

- `src/core/upload/cpa_upload.py` - CPA 上传逻辑
- `test_cpa_format.py` - 测试脚本
- `fix_missing_account_id.py` - 修复脚本

## 更新日志

- 2026-04-03: 添加 `chatgpt_account_id` 字段支持
- 2026-04-03: 创建测试和修复脚本
