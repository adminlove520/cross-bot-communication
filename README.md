# Cross-Bot Communication Skill

> 跨 Bot 通信的通用解决方案

## 问题背景

在 Telegram 群聊中，存在一个技术限制：**Bot 无法收到其他 Bot 发送的消息**（除非对方是管理员）。

本 Skill 提供了一套通用的解决方案，帮助你正确地与其他 Bot 进行通信。

## 核心原理

### Telegram Bot 限制

```
人类发送消息 → Bot A 可以收到 ✅
Bot A 发送消息 → Bot B 无法收到 ❌ (普通成员)
Bot A 发送消息 → Bot B 可以收到 ✅ (Bot A 是管理员)
```

### 解决方案

| 方案 | 适用场景 | 成功率 |
|------|----------|--------|
| 频道中转 | 目标 bot 在频道 | 高 |
| 管理员转发 | 目标 bot 是群管理员 | 高 |
| sessions_send | 对方在线 | 中 |
| GitHub Discussion | 异步通信 | 100% |

## 使用方法

### 1. 检测群成员

使用 Telegram Bot API 获取群成员：

```bash
# 获取群管理员
GET https://api.telegram.org/bot<TOKEN>/getChatAdministrators?chat_id=<GROUP_ID>
```

### 2. 验证目标 Bot 状态

```python
def check_bot_status(bot_username, chat_id, token):
    """检查 Bot 在群中的状态"""
    # 1. 获取群成员
    members = get_chat_members(chat_id, token)
    
    # 2. 查找目标 bot
    bot = find_member(bot_username, members)
    
    if not bot:
        return {"status": "not_in_group"}
    
    if bot.is_admin:
        return {"status": "admin", "can_receive": True}
    else:
        return {"status": "member", "can_receive": False}
```

### 3. 选择通信方式

```python
def select_communication_method(target_bot, channel_id=None):
    """根据目标 bot 状态选择最佳通信方式"""
    
    if target_bot["can_receive"]:
        return "direct_mention"  # 直接艾特
    
    if channel_id and target_bot["in_channel"]:
        return "channel_forward"  # 频道中转
    
    return "async_message"  # 异步方式 (GitHub Discussion)
```

## 配置

### 必需配置

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "default_channel_id": "YOUR_DEFAULT_CHANNEL_ID"
}
```

### 可选配置

```json
{
  "known_bots": {
    "@bot1": {"name": "Bot 1", "in_channel": true},
    "@bot2": {"name": "Bot 2", "in_channel": false}
  }
}
```

## 完整流程图

```
发送消息前检查:
    │
    ├─ 目标 bot 是谁？
    │
    ├─ 在当前群吗？
    │   ├─ 否 → 使用频道中转 / GitHub Discussion
    │   │
    │   └─ 是 → 是管理员吗？
    │           ├─ 是 → 直接艾特 ✅
    │           └─ 否 → 频道中转 / GitHub Discussion
    │
    └─ 发送消息
```

## 常见问题

### Q: 为什么 Bot 无法收到其他 Bot 的消息？

A: 这是 Telegram 的设计限制，防止 Bot 之间产生无限消息循环。

### Q: 频道中转一定可行吗？

A: 取决于目标 Bot 是否也在同一个频道。如果是，可以使用频道中转。

### Q: 如何验证对方是本人？

A: 可以要求对方在特定频道发送特定格式的消息来验证身份。

## 更新日志

- 2026-03-12: 初始版本
