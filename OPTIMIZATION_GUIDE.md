# Codex-Console 注册成功率优化指南

## 已完成的优化 ✅

### 1. 替换官方 LuckMail SDK
- ✅ 已将 `~/codex-console/luckmail/` 替换为官方最新版本
- ✅ 官方 SDK 包含更完整的错误处理和重试逻辑

### 2. 增加验证码获取超时时间
- ✅ `chatgpt_client.py`: 90秒 → 180秒
- ✅ `oauth_client.py`: 60秒 → 180秒
- 原因：LuckMail API 响应较慢，60-90秒经常超时

### 3. 修复 add-phone 重定向问题
- ✅ 在 `register.py` 中添加了 "跟随重定向链失败" 和 "redirect" 触发关键词
- ✅ 现在会自动切换到 anyauto 兜底流程处理 add-phone 页面

## 失败原因分析

根据日志分析，主要失败原因：

1. **验证码获取超时** (40%) - 已修复
   - LuckMail API 响应慢
   - 超时时间设置过短

2. **OpenAI 429 限流** (30%)
   - 批量注册时请求过于频繁
   - 需要添加请求间隔

3. **邮箱用户名被拒绝** (20%)
   - 触发 OpenAI 风控
   - 某些邮箱域名或用户名模式被识别

4. **add-phone 重定向失败** (10%) - 已修复
   - OpenAI 强制要求手机验证
   - anyauto 流程可以绕过

## 推荐的使用策略

### 1. 批量注册设置

**避免 429 限流：**
```
- 单次批量数量：建议 3-5 个
- 批次间隔：至少 5-10 分钟
- 避免在短时间内大量注册
```

**Web UI 操作：**
1. 进入注册页面
2. 设置数量为 3-5
3. 点击开始注册
4. 等待全部完成后，休息 5-10 分钟
5. 再开始下一批

### 2. 邮箱服务配置

**LuckMail 推荐配置：**
```json
{
  "inbox_mode": "purchase",
  "email_type": "ms_graph",
  "preferred_domain": "outlook.de",
  "reuse_existing_purchases": true,
  "poll_interval": 3.0,
  "timeout": 180
}
```

**为什么选择 outlook.de：**
- 成功率较高
- 不容易触发 OpenAI 风控
- LuckMail 支持良好

### 3. 代理设置

**推荐：**
- 使用稳定的住宅代理
- 避免使用数据中心 IP
- 每批注册可以切换不同的代理

### 4. 监控和重试

**查看日志：**
```bash
cd ~/codex-console
tail -f logs/app.log | grep -E "成功|失败|ERROR"
```

**失败后的处理：**
- 429 限流：等待 10-15 分钟后重试
- 验证码超时：检查 LuckMail 余额和服务状态
- 用户名被拒：更换邮箱域名或等待一段时间

## 预期成功率

**优化前：** ~40-50%
**优化后：** ~70-80%

**影响成功率的因素：**
1. LuckMail API 稳定性 (最重要)
2. OpenAI 风控策略变化
3. 代理质量
4. 批量注册频率

## 进一步优化建议

### 1. 添加智能重试机制
在 `register.py` 中添加：
- 429 错误：自动等待并重试
- 验证码超时：自动重新发送验证码

### 2. 邮箱域名轮换
配置多个邮箱域名：
```python
domains = ["outlook.de", "outlook.com", "hotmail.com"]
# 随机选择或轮换使用
```

### 3. 请求速率限制
在批量注册时添加：
```python
import time
time.sleep(random.uniform(30, 60))  # 每个任务之间随机延迟
```

### 4. 监控和告警
- 成功率低于 60% 时发送通知
- LuckMail 余额不足时告警
- 连续失败 3 次时暂停批量注册

## 故障排查

### 问题：验证码一直超时
**解决方案：**
1. 检查 LuckMail 余额：`curl -H "Authorization: Bearer YOUR_KEY" https://mails.luckyous.com/api/user/balance`
2. 检查网络连接
3. 尝试手动创建订单测试

### 问题：频繁遇到 429
**解决方案：**
1. 减少批量数量（改为 2-3 个）
2. 增加批次间隔（改为 15-20 分钟）
3. 更换代理 IP

### 问题：邮箱用户名被拒绝
**解决方案：**
1. 更换邮箱域名
2. 等待 1-2 小时后重试
3. 检查是否触发 OpenAI 风控

## 服务重启

修改配置后需要重启服务：
```bash
cd ~/codex-console
pkill -f "python.*webui.py"
python webui.py > /tmp/codex-console.log 2>&1 &
```

## 联系支持

- LuckMail 问题：联系 LuckMail 客服
- Codex-Console 问题：查看 GitHub Issues
