# Cross-Bot Communication Skill

> 跨 Bot 通信的智能解决方案 - 零配置自动检测

## 核心原理

### Telegram```
人类发 Bot 限制

消息 → Bot A 能收到 ✅
Bot A 发消息 → Bot B 无法收到 ❌ (普通成员)
Bot A 发消息 → Bot B 能收到 ✅ (Bot A 是管理员)
```

### 智能解决方案

用户只需做一件事：**把 Bot 拉进群/频道**

其他全部**自动完成**！

---

## 自动检测流程

### 1. 获取群/频道成员

使用 Telegram Bot API 自动获取：

```bash
# 获取成员数量
GET https://api.telegram.org/bot<TOKEN>/getChatMembersCount?chat_id=<ID>

# 获取管理员列表
GET https://api.telegram.org/bot<TOKEN>/getChatAdministrators?chat_id=<ID>

# 获取成员列表
GET https://api.telegram.org/bot<TOKEN>/getChatMember?chat_id=<ID>&user_id=<USER_ID>
```

### 2. 自动识别 Bot

遍历群成员，根据以下特征识别 Bot：
- `user.is_bot = true`
- 用户名以 `_bot` 结尾

### 3. 自动记录信息

自动构建已知 Bot 数据库：

```json
{
  "@bot1": {
    "name": "Bot 1",
    "groups": ["GROUP_ID_1"],
    "channels": ["CHANNEL_ID_1"],
    "admin_of": ["GROUP_ID_2"]
  }
}
```

### 4. 智能选择通信方式

| 目标 Bot 状态 | 通信方式 |
|--------------|---------|
| 是当前群管理员 | 直接艾特 ✅ |
| 在同一频道 | 频道中转 ✅ |
| 不在任何共同群/频道 | GitHub Discussion / sessions_send |

---

## 使用方法

### 场景 1: 在群里发现新 Bot

当有新 Bot 加入群时，Skill 自动：
1. 检测到新成员
2. 获取其信息（用户名、是否管理员）
3. 更新已知 Bot 列表

### 场景 2: 想联系某个 Bot

```
用户: "联系小敏"
↓
Skill 自动检查:
  - 小敏在当前群吗？ → 否
  - 小敏在 OpenDiskHub 频道吗？ → 是
  - 使用频道中转 → 发送消息到频道并 @小敏
```

### 场景 3: 不确定对方身份

```
用户: "确认这是小隐吗？"
↓
Skill 自动:
  - 获取小隐在当前群的信息
  - 检查是否是管理员
  - 返回验证结果
```

---

## 零配置设计

### 用户需要做的

| 操作 | 说明 |
|------|------|
| 添加 Bot 到群 | 只需这一步 |
| 添加 Bot 到频道 | 只需这一步 |

### 自动完成的

| 功能 | 说明 |
|------|------|
| 识别 Bot | 自动检测 |
| 获取信息 | API 自动获取 |
| 记录状态 | 本地/内存自动存储 |
| 选择方案 | 根据状态智能选择 |

---

## 配置 (可选)

如果需要特殊配置：

```json
{
  "fallback_channel": "DEFAULT_CHANNEL_ID",
  "fallback_method": "github_discussion"
}
```

---

## 常见问题

### Q: 需要 bot token 吗？

A: **不需要**！使用当前 Bot 的 token 自动完成所有检测。

### Q: 需要手动配置群 ID 吗？

A: **不需要**！当 Bot 在群里时，API 自动返回群信息。

### Q: 如何知道有哪些 Bot？

A: 自动检测！当用户说"联系 XX"时，Skill 会自动在已知 Bot 中查找。

---

## 更新日志

- 2026-03-12: 初始版本 - 零配置自动检测
