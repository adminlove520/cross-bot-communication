# Cross-Bot Communication

> 跨 Bot 通信的通用解决方案

## 功能

- 检测 Telegram 群/频道中的 Bot 成员
- 验证 Bot 身份和状态（管理员/普通成员）
- 自动选择最佳通信方式
- 支持配置化管理

## 核心原则

**Telegram Bot 无法收到其他 Bot 发送的消息**（除非是管理员）

## 使用

### 检查群成员

```bash
# 使用 Telegram Bot API
curl "https://api.telegram.org/bot<TOKEN>/getChatAdministrators?chat_id=<GROUP_ID>"
```

### 通信方式选择

| 目标 Bot 状态 | 推荐方式 |
|--------------|---------|
| 是群管理员 | 直接艾特 |
| 在同一频道 | 频道中转 |
| 其他 | GitHub Discussion / sessions_send |

## 配置

在 `config.json` 中配置：

```json
{
  "bot_token": "YOUR_TOKEN",
  "default_channel": "CHANNEL_ID"
}
```

## 更新日志

- 2026-03-12: 初始版本 - 通用跨 Bot 通信方案
