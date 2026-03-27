# Cross-Bot Communication

> 跨 Bot 通信的智能解决方案 - 让 AI 助手之间无缝协作

## 功能

- ✅ **意图解析** - 自动从自然语言中提取目标、动作、消息和紧急程度
- ✅ **关系管理** - 持久化的 Bot 社交关系表，支持增删改查
- ✅ **可达性检查** - 自动检测 Privacy Mode / 管理员 / 群组 / 频道等条件
- ✅ **诚实告知** - 找不到就说找不到，并给出建议方案
- ✅ **零配置启动** - 将 Bot 拉入群组即可自动绑定
- ✅ **JSON 输出** - 所有操作支持结构化输出，方便龙虾调用

## 快速开始

### 安装

```bash
git clone https://github.com/adminlove520/cross-bot-communication.git
cd cross-bot-communication
```

### 配置

编辑 `config.json`，添加已知的 Bot 关系：

```json
{
  "relations": [
    {
      "owner_id": "风",
      "owner_name": "风",
      "bot_username": "@caddycherrybot",
      "bot_name": "小溪",
      "groups": ["-1003702841996"],
      "channels": ["-1003658967414"],
      "is_admin": false,
      "privacy_mode": false
    }
  ]
}
```

### 使用

```bash
# 发送跨 Bot 消息
python main.py send "联系小敏，让它主人明天开会"

# 检查 Bot 可达性
python main.py check 小敏

# 列出所有 Bot
python main.py list

# 解析意图 (调试)
python main.py parse "通知小隐，明天要开会"

# JSON 输出
python main.py send "联系小敏" --json
```

### Python API

```python
from src.bot_comm import BotCommunicator

comm = BotCommunicator(config_path="config.json")

# 处理用户消息
result = comm.process_message("联系小敏，让它主人明天开会")
print(result.success)    # True
print(result.message)    # "已准备消息..."
print(result.to_json())  # 完整 JSON

# 检查可达性
info = comm.check_bot("小敏")

# 管理 Bot
comm.add_bot("@new_bot", "小新", "主人名", groups=["-100xxx"])
comm.remove_bot("@old_bot")
```

## 架构

```
用户消息 → IntentParser(意图解析)
         → RelationManager(关系查询)
         → BotCommunicator(决策+消息构建)
         → 目标 Bot (通过群组/频道中转)
```

## 项目结构

```
cross-bot-communication/
├── src/
│   ├── bot_comm.py           # 通信核心引擎
│   ├── intent_parser.py      # 意图解析器
│   └── relation_manager.py   # 关系管理器
├── main.py                   # CLI 入口
├── config.json               # 关系配置
└── requirements.txt          # 依赖
```

## License

MIT

## 作者

- GitHub: [@adminlove520](https://github.com/adminlove520)
