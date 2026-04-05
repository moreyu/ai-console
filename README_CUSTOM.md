# Codex Console - 定制版本

基于 [dou-jiang/codex-console](https://github.com/dou-jiang/codex-console) 的定制版本，增强了 OpenAI 账号管理和 Cliproxy API 集成功能。

## 原项目信息

- **原始仓库**: https://github.com/dou-jiang/codex-console
- **原始功能**: OpenAI 账号注册和管理工具

## 主要改动

### 1. 核心功能增强

#### 1.1 OAuth 客户端优化 (`src/core/anyauto/oauth_client.py`)
- ✅ 修复了 refresh token 提取逻辑
- ✅ 增强了 session token 支持
- ✅ 改进了错误处理和日志记录
- ✅ 添加了自动重试机制

#### 1.2 ChatGPT 客户端改进 (`src/core/anyauto/chatgpt_client.py`)
- ✅ 优化了登录流程
- ✅ 增强了 token 管理
- ✅ 改进了会话保持机制

#### 1.3 注册流程优化 (`src/core/register.py`)
- ✅ 修复了 refresh token 在注册时丢失的问题
- ✅ 增强了账号验证流程
- ✅ 改进了错误恢复机制

#### 1.4 CPA 上传功能 (`src/core/upload/cpa_upload.py`)
- ✅ 添加了 Cliproxy API 支持
- ✅ 优化了批量上传逻辑
- ✅ 增强了错误处理

#### 1.5 配置管理 (`src/config/settings.py`)
- ✅ 添加了 Cliproxy API 配置
- ✅ 优化了环境变量管理
- ✅ 增强了配置验证

### 2. 新增工具脚本

#### 2.1 批量管理工具
- **`batch_relogin.py`** - 批量重新登录账号，刷新 token
- **`batch_upload_new_accounts.py`** - 批量上传新注册的账号到 Cliproxy
- **`simple_batch_register.py`** - 简化的批量注册工具

#### 2.2 导出工具
- **`export_cpa_json.py`** - 导出 CPA 格式的账号 JSON
- **`export_full_format.py`** - 导出完整格式的账号信息
- **`export_with_id_token.py`** - 导出包含 ID token 的账号信息

#### 2.3 Token 管理工具
- **`extract_refresh_token_from_session.py`** - 从 session token 提取 refresh token
- **`update_tokens_from_browser.py`** - 从浏览器更新 token
- **`manual_refresh_token_guide.py`** - 手动刷新 token 指南

#### 2.4 上传工具
- **`reupload_to_cliproxy.py`** - 重新上传账号到 Cliproxy
- **`reupload_to_cpa.py`** - 重新上传账号到 CPA
- **`reupload_with_service.py`** - 使用服务上传账号

#### 2.5 测试工具
- **`test_cliproxy_upload.py`** - 测试 Cliproxy 上传功能
- **`test_cpa_format.py`** - 测试 CPA 格式
- **`test_session_endpoint.py`** - 测试 session 端点
- **`generate_test_formats.py`** - 生成测试格式

#### 2.6 其他工具
- **`fix_missing_account_id.py`** - 修复缺失的 account_id
- **`team_invite.py`** - 团队邀请管理

### 3. 文档增强

新增了详细的问题解决文档：

- **`CLIPROXY_FIX.md`** - Cliproxy 集成问题修复指南
- **`CLIPROXY_SESSION_TOKEN_SUPPORT.md`** - Session token 支持文档
- **`REFRESH_TOKEN_ISSUE.md`** - Refresh token 问题分析
- **`FIX_REFRESH_TOKEN_IN_REGISTRATION.md`** - 注册时 refresh token 修复
- **`FINAL_SOLUTION.md`** - 最终解决方案
- **`FINAL_CONCLUSION.md`** - 项目总结
- **`OPTIMIZATION_GUIDE.md`** - 优化指南

### 4. LuckMail 集成

- ✅ 集成了 LuckMail SDK 用于邮箱验证
- ✅ 自动获取验证码
- ✅ 支持批量邮箱管理

### 5. 数据导出功能

新增了多种导出格式：

- **CPA 格式** - 兼容 CPA 系统
- **完整格式** - 包含所有 token 信息
- **ID Token 格式** - 包含 ID token 的格式

## 环境配置

### 必需的环境变量

```bash
# OpenAI 配置
OPENAI_EMAIL=your_email@example.com
OPENAI_PASSWORD=your_password

# Cliproxy API 配置
CLIPROXY_API_URL=https://your-cliproxy-api.com
CLIPROXY_API_KEY=your_api_key

# LuckMail 配置
LUCKMAIL_API_KEY=your_luckmail_key
```

### 配置文件

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

## 安装和使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，填写必要的配置。

### 3. 运行主程序

```bash
python webui.py
```

访问 http://localhost:5000 使用 Web 界面。

### 4. 使用批量工具

#### 批量注册账号

```bash
python simple_batch_register.py
```

#### 批量上传到 Cliproxy

```bash
python batch_upload_new_accounts.py
```

#### 批量重新登录

```bash
python batch_relogin.py
```

#### 导出账号信息

```bash
# 导出 CPA 格式
python export_cpa_json.py

# 导出完整格式
python export_full_format.py

# 导出包含 ID token
python export_with_id_token.py
```

## 数据目录

- **`data/`** - 数据库和配置文件
- **`cpa_exports/`** - CPA 格式导出文件
- **`cpa_exports_full/`** - 完整格式导出文件
- **`logs/`** - 日志文件

## 主要修复的问题

### 1. Refresh Token 丢失问题

**问题**: 注册时 refresh token 没有正确保存到数据库

**解决方案**:
- 修改了 `src/core/register.py` 中的注册流程
- 确保在注册成功后立即提取并保存 refresh token
- 详见 `FIX_REFRESH_TOKEN_IN_REGISTRATION.md`

### 2. Session Token 支持

**问题**: 原版不支持使用 session token

**解决方案**:
- 在 `src/core/anyauto/oauth_client.py` 中添加了 session token 支持
- 可以从 session token 提取 refresh token
- 详见 `CLIPROXY_SESSION_TOKEN_SUPPORT.md`

### 3. Cliproxy API 集成

**问题**: 原版不支持 Cliproxy API

**解决方案**:
- 在 `src/core/upload/cpa_upload.py` 中添加了 Cliproxy API 支持
- 支持批量上传账号到 Cliproxy
- 详见 `CLIPROXY_FIX.md`

### 4. 批量操作优化

**问题**: 原版批量操作不够完善

**解决方案**:
- 添加了多个批量操作脚本
- 改进了错误处理和重试机制
- 添加了详细的日志记录

## 技术栈

- **Python 3.9+**
- **Flask** - Web 框架
- **SQLAlchemy** - ORM
- **Playwright** - 浏览器自动化
- **LuckMail SDK** - 邮箱验证
- **Requests** - HTTP 客户端

## 注意事项

1. **账号安全**: 请妥善保管 `.env` 文件，不要提交到 Git
2. **API 限制**: 注意 OpenAI 和 Cliproxy 的 API 调用限制
3. **批量操作**: 批量操作时建议设置合理的延迟，避免触发反爬虫
4. **Token 管理**: 定期刷新 token，避免过期

## 故障排除

### 问题 1: Refresh token 为空

**解决方案**: 使用 `extract_refresh_token_from_session.py` 从 session token 提取

### 问题 2: 上传到 Cliproxy 失败

**解决方案**: 检查 API key 和 URL 配置，查看 `CLIPROXY_FIX.md`

### 问题 3: 批量注册失败

**解决方案**: 检查邮箱配置，确保 LuckMail API 正常工作

## 更新日志

### 2026-04-03
- ✅ 修复 refresh token 丢失问题
- ✅ 添加 Cliproxy API 支持
- ✅ 添加批量管理工具
- ✅ 优化 token 管理流程

### 2026-04-04
- ✅ 添加团队邀请功能
- ✅ 优化导出格式
- ✅ 改进错误处理

## 贡献者

- 基于 [dou-jiang/codex-console](https://github.com/dou-jiang/codex-console)
- 定制和增强: Moreyu

## 许可证

继承原项目许可证。

## 相关链接

- 原始项目: https://github.com/dou-jiang/codex-console
- Cliproxy API 文档: (根据实际情况填写)
- LuckMail SDK: (根据实际情况填写)
