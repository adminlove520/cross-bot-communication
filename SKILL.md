# Cross-Bot Communication

> 跨 Bot 通信的智能解决方案

---

## 架构

```
用户 → subagent(监听) → 主agent(决策) → subagent(执行) → 目标Bot
```

**核心："记忆在哪里不重要，重要的是能调用"**

---

## 功能

- ✅ 零配置自动检测
- ✅ subagent 自动监听群消息
- ✅ 自动识别"联系XXX"意图
- ✅ 关系绑定 (主人 ↔ bot)
- ✅ 智能通信方式选择
- ✅ 找不到时诚实告知
- ✅ **Privacy Mode 自动检查**

---

## Privacy Mode 检查

### 什么是 Privacy Mode？

Privacy Mode 关闭时，Bot 可以在群里被艾特并自动响应。

### 自动检查流程

```
1. subagent 收到 @消息
   ↓
2. 检查 Privacy Mode 状态
   ↓
3. 如果开启 → 礼貌告知无法自动回复
   ↓
4. 如果关闭 → 正常处理
```

### Privacy Mode 开启时的响应

```
"抱歉，我目前开启了 Privacy Mode，无法自动回复群消息。

如需帮助，请私信我的主人 @username 或自行联系。

关闭 Privacy Mode 后我可以自动响应群消息～"
```

### 检查方法

```python
# 在 OpenClaw 中检查 Privacy Mode
# 通过 config 或 session 配置检查

def check_privacy_mode(bot_username):
    # 查询该 bot 的隐私设置
    return privacy_mode_enabled
```

---

## 硬性条件

| 条件 | 状态 | 处理 |
|------|------|------|
| Privacy Mode 关闭 | ✅ | 正常处理 |
| 同一群 | ✅ | 可尝试 |
| 是管理员 | ✅ | 直接艾特 |
| 同一频道 | ✅ | 频道中转 |
| 都不满足 | ❌ | 诚实告知 |

---

## 自动化流程

### 1. subagent 监听配置

```yaml
# subagent 配置
name: cross-bot-listener
triggers:
  - "@caddycherrybot"
actions:
  - check_privacy_mode  # 先检查隐私模式
  - forward_to_main      # 然后转发
```

### 2. 意图识别

当 subagent 收到包含以下关键词的消息时，自动转发给主 agent：

- "联系"
- "@其他bot"
- "帮忙"
- "通知"

### 3. 关系表

```json
{
  "relations": [
    {
      "owner_id": "风",
      "bot_username": "@caddycherrybot",
      "bot_name": "小溪",
      "groups": ["-1003702841996"],
      "channels": ["-1003658967414"],
      "is_admin": false,
      "privacy_mode": false
    },
    {
      "owner_id": "千里",
      "bot_username": "@YinxiaBot",
      "bot_name": "小隐",
      "groups": ["-1003702841996"],
      "channels": ["-1003658967414"],
      "is_admin": false,
      "privacy_mode": false
    },
    {
      "owner_id": "小灵",
      "bot_username": "@ikunge_bot",
      "bot_name": "小敏",
      "groups": ["-1003702841996"],
      "channels": ["-1003658967414"],
      "is_admin": false,
      "privacy_mode": false
    }
  ]
}
```

### 4. 消息模板

```
收到消息: "联系小敏，让它主人明天开会"

自动解析:
- 目标: 小敏 (@ikunge_bot)
- 内容: 让它主人明天开会
- 发送方式: 频道中转 (@OpenDiskHub)

自动发送:
"@ikunge_bot 通知：主人的AI让你主人明天开会"
```

---

## 安装

1. 复制 skills/cross-bot-communication 到 OpenClaw skills 目录
2. 配置 subagent 监听群消息
3. 启动 subagent 自动处理

---

## 更新日志

- 2026-03-12: 添加 Privacy Mode 自动检查功能
- 2026-03-12: 优化为自动化版本，添加 subagent 监听配置
