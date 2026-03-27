# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-27

### Added
- **完整 Python 实现** - 从纯文档升级为可运行的代码项目
- `src/bot_comm.py` - 跨 Bot 通信核心引擎
- `src/intent_parser.py` - 自然语言意图解析器 (支持中英文)
- `src/relation_manager.py` - 社交关系管理器 (支持持久化)
- `main.py` - CLI 命令行工具
- **意图解析** - 自动从用户消息中提取: 目标 Bot、动作类型、消息内容、紧急程度
- **可达性检查** - 自动检查通信条件 (Privacy Mode / 管理员 / 群组 / 频道)
- **诚实告知** - 条件不满足时提供具体建议方案
- **群组扫描** - `scan_groups()` 自动发现群组中的 Bot 并构建关系
- **JSON 输出** - 所有命令支持 `--json` 参数，方便龙虾程序化调用
- `config.json` - 预配置的关系表
- `requirements.txt` - 依赖声明
- 更新 `_meta.json` 版本到 1.0.0

### Changed
- SKILL.md 增加实际代码示例
- README.md 增加 CLI 使用说明

---

## [0.1.0] - 2026-03-12

### Added
- 初始版本 (仅文档和架构设计)
- Telegram Bot 限制说明
- 通信方式选择逻辑
- 通用检测方法
- 配置模板
