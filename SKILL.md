# Cross-Bot Communication

> 跨 Bot 通信的智能解决方案 - 可运行的完整实现

## 触发词

- "联系"、"通知"、"传话"、"转告"
- "cross bot"、"bot communication"
- "@某个bot"

## 架构

```
用户消息 → IntentParser(解析意图)
         → RelationManager(查询关系)
         → BotCommunicator(决策+执行) → 目标Bot
```

**核心原则：**
- **诚实** - 找不到就是找不到，不编造
- **零配置** - 用户只需把 Bot 拉进群，其他自动完成
- **解耦** - 决策层(主agent) 与执行层(subagent) 分离

## 使用方法

### Python API (龙虾推荐)

```python
from src.bot_comm import BotCommunicator

comm = BotCommunicator(config_path="config.json")

# 发送消息
result = comm.process_message("联系小敏，让它主人明天开会")
print(result.to_json())

# 检查可达性
info = comm.check_bot("小敏")

# 列出所有 Bot
bots = comm.list_bots()

# 添加新 Bot
comm.add_bot("@new_bot", "小新", "主人名", groups=["-100xxx"])
```

### CLI 命令行

```bash
# 发送消息
python main.py send "联系小敏，让它主人明天开会"

# 检查 Bot
python main.py check 小敏

# 列出 Bot
python main.py list

# JSON 输出 (适合程序调用)
python main.py send "通知小隐，明天要开会" --json
```

## 意图解析示例

```
输入: "联系小敏，让它主人明天开会"

解析结果:
  action: "contact"
  target: "小敏"
  message: "让它主人明天开会"
  urgency: "normal"
  confidence: 0.7
```

## 可达性检查

| 条件 | 状态 | 处理 |
|------|------|------|
| Privacy Mode 关闭 | ✅ | 正常处理 |
| Bot 在同一群 | ✅ | 群内 @ 提醒 |
| Bot 是管理员 | ✅ | 直接艾特 |
| Bot 在同一频道 | ✅ | 频道中转 |
| 都不满足 | ❌ | 诚实告知 + 建议方案 |

## 诚实告知示例

```
"抱歉，没有可用的通信方式

建议方案：
  1. 关闭小敏的 Privacy Mode
  2. 将小敏设为群管理员
  3. 将两个 Bot 拉入同一群组"
```

## 项目结构

```
cross-bot-communication/
├── src/
│   ├── __init__.py           # 包入口
│   ├── bot_comm.py           # 通信核心引擎
│   ├── intent_parser.py      # 意图解析器
│   └── relation_manager.py   # 关系管理器
├── main.py                   # CLI 入口
├── config.json               # 关系配置表
├── config.example.json       # 配置模板
├── _meta.json                # 项目元信息
├── requirements.txt          # 依赖
├── SKILL.md                  # 技能描述 (本文件)
├── README.md                 # 项目文档
└── CHANGELOG.md              # 更新日志
```

## 示例对话

**用户**: 联系小敏，让它告诉主人明天要开会
**龙虾**: 调用 `comm.process_message(...)` → 构建消息 → 返回结果

**用户**: 小隐还在吗？帮我通知它一声
**龙虾**: 调用 `comm.check_bot("小隐")` → 检查可达性 → 选择通信方式
