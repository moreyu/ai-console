# Cliproxy 适配 OpenAI 新 OAuth 流程

## 问题描述

OpenAI 已经改变了 OAuth 流程，不再在标准授权流程中返回 `refresh_token`。这导致 Cliproxy 无法使用 `refresh_token` 来刷新 token 和查询 Codex 配额。

## 当前情况

从 codex-console 注册的账号包含：
- ✅ `access_token` - 访问令牌（有效期约 10 天）
- ✅ `session_token` - 会话令牌（长期有效）
- ✅ `account_id` / `chatgpt_account_id` - 账号 ID
- ❌ `refresh_token` - OpenAI 不再提供

## Cliproxy 需要的修改

### 1. 支持使用 session_token 刷新 access_token

**当前逻辑：**
```
使用 refresh_token 调用 https://auth.openai.com/oauth/token 刷新
```

**需要改为：**
```
如果有 session_token：
  1. 使用 session_token 设置 Cookie: __Secure-next-auth.session-token
  2. 调用 https://chatgpt.com/api/auth/session
  3. 从响应中获取新的 access_token

如果有 refresh_token（向后兼容）：
  使用原有的 OAuth refresh_token 流程
```

### 2. 修改 Codex 凭证验证逻辑

**当前逻辑：**
```
检查是否有 refresh_token，没有则报错"缺少 ChatGPT 账号 ID"
```

**需要改为：**
```
检查是否有 session_token 或 refresh_token
如果都没有，才报错
```

### 3. 示例代码（Go）

```go
// RefreshAccessToken 刷新 access token
func (c *CodexAuth) RefreshAccessToken() error {
    // 优先使用 session_token
    if c.SessionToken != "" {
        return c.refreshBySessionToken()
    }

    // 回退到 refresh_token（向后兼容）
    if c.RefreshToken != "" {
        return c.refreshByRefreshToken()
    }

    return errors.New("no session_token or refresh_token available")
}

// refreshBySessionToken 使用 session_token 刷新
func (c *CodexAuth) refreshBySessionToken() error {
    client := &http.Client{Timeout: 30 * time.Second}

    req, err := http.NewRequest("GET", "https://chatgpt.com/api/auth/session", nil)
    if err != nil {
        return err
    }

    // 设置 session_token cookie
    req.AddCookie(&http.Cookie{
        Name:  "__Secure-next-auth.session-token",
        Value: c.SessionToken,
    })

    req.Header.Set("Accept", "application/json")
    req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != 200 {
        return fmt.Errorf("session refresh failed: %d", resp.StatusCode)
    }

    var session struct {
        AccessToken string `json:"accessToken"`
        Expires     string `json:"expires"`
    }

    if err := json.NewDecoder(resp.Body).Decode(&session); err != nil {
        return err
    }

    c.AccessToken = session.AccessToken
    // 解析 expires 并更新过期时间

    return nil
}
```

## 测试方法

### 1. 准备测试数据

使用 codex-console 导出的 JSON 文件：

```json
{
  "type": "codex",
  "email": "test@example.com",
  "account_id": "75987746-6a22-4674-b853-8a8983d13921",
  "chatgpt_account_id": "75987746-6a22-4674-b853-8a8983d13921",
  "access_token": "eyJhbGci...",
  "session_token": "eyJhbGci...",
  "refresh_token": "",
  "id_token": "",
  "expired": "",
  "last_refresh": ""
}
```

### 2. 上传到 Cliproxy

```bash
curl -X POST https://cliproxy.moreyu.eu.org/v0/management/auth-files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test@example.com.json"
```

### 3. 验证

1. 检查账号是否显示为 `active` 状态
2. 检查 Codex 配额是否正常显示
3. 尝试使用账号发送请求

## 向后兼容性

修改后的 Cliproxy 应该同时支持：
- ✅ 新格式：有 `session_token`，没有 `refresh_token`
- ✅ 旧格式：有 `refresh_token`，没有 `session_token`
- ✅ 完整格式：同时有 `session_token` 和 `refresh_token`

## 相关文件

- `codex-console/REFRESH_TOKEN_ISSUE.md` - 问题分析文档
- `codex-console/extract_refresh_token_from_session.py` - 尝试提取 refresh_token 的脚本
- `codex-console/test_cliproxy_upload.py` - 测试上传脚本

## 时间线

- 2026-04-03: 发现问题 - Cliproxy 显示"缺少 ChatGPT 账号 ID"
- 2026-04-03: 确认根本原因 - OpenAI 不再返回 `refresh_token`
- 2026-04-03: 提出解决方案 - Cliproxy 需要支持 `session_token`

## 联系方式

如需协助修改 Cliproxy 代码，请提供：
1. Cliproxy 源码仓库地址
2. 当前使用的 Cliproxy 版本
3. 是否有修改权限
