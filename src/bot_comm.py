"""
Bot 通信核心 - 跨 Bot 消息传递引擎
"""

import json
import time
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

from .relation_manager import RelationManager, BotRelation
from .intent_parser import IntentParser, CommIntent

logger = logging.getLogger("cross-bot-comm")


@dataclass
class CommResult:
    """通信操作结果"""
    success: bool
    message: str
    method: str = ""        # 使用的通信方式
    target_bot: str = ""    # 目标 Bot
    sent_message: str = ""  # 发出的消息
    details: Dict = None

    def to_json(self) -> str:
        d = asdict(self)
        if d["details"] is None:
            d["details"] = {}
        return json.dumps(d, ensure_ascii=False, indent=2)

    def to_dict(self) -> Dict:
        d = asdict(self)
        if d["details"] is None:
            d["details"] = {}
        return d


class BotCommunicator:
    """跨 Bot 通信引擎

    架构:
        用户消息 → IntentParser(解析) → RelationManager(查询)
                → BotCommunicator(决策+执行) → 目标 Bot

    使用方式:
        comm = BotCommunicator(config_path="config.json")
        result = comm.process_message("联系小敏，让它主人明天开会")
    """

    def __init__(self, config_path: str = None):
        self.relations = RelationManager(config_path)
        self.parser = IntentParser()
        self.message_log: List[Dict] = []

    # ==================== 核心流程 ====================

    def process_message(self, text: str, sender_id: str = "") -> CommResult:
        """处理用户消息 - 主入口

        流程:
        1. 解析意图 (IntentParser)
        2. 查找目标 Bot (RelationManager)
        3. 检查可达性
        4. 选择通信方式
        5. 构建消息
        6. 返回结果 (或执行发送)
        """
        # 1. 解析意图
        intent = self.parser.parse(text)
        if intent.action == "unknown" or not intent.target:
            return CommResult(
                success=False,
                message="无法识别通信意图，请明确指定目标和内容",
                details={"parsed": asdict(intent)},
            )

        logger.info(f"解析意图: {intent.action} -> {intent.target}: {intent.message}")

        # 2. 检查可达性
        reachability = self.relations.check_reachability(intent.target)
        if not reachability["reachable"]:
            return CommResult(
                success=False,
                message=self._format_unreachable(reachability),
                target_bot=intent.target,
                details=reachability,
            )

        # 3. 选择最佳通信方式
        method = reachability["recommended"]
        bot_info = reachability["bot"]

        # 4. 构建消息
        formatted_msg = self._build_message(intent, bot_info, sender_id)

        # 5. 记录日志
        self._log_message(intent, method, formatted_msg)

        # 6. 返回结果 (实际发送由外部 Telegram API 执行)
        return CommResult(
            success=True,
            message=f"已准备消息，通过 {method['method']} 发送给 {bot_info['bot_name']}",
            method=method["method"],
            target_bot=bot_info["bot_username"],
            sent_message=formatted_msg,
            details={
                "intent": asdict(intent),
                "method": method,
                "bot_info": bot_info,
            },
        )

    # ==================== 消息构建 ====================

    def _build_message(self, intent: CommIntent, bot_info: Dict, sender_id: str = "") -> str:
        """根据意图和方式构建消息"""
        bot_name = bot_info.get("bot_name", "")
        bot_username = bot_info.get("bot_username", "")

        prefix = f"@{bot_username.lstrip('@')}" if bot_username else bot_name

        if intent.action == "notify":
            return f"{prefix} 通知：{intent.message}"
        elif intent.action == "ask":
            return f"{prefix} 请问：{intent.message}"
        else:
            return f"{prefix} 消息：{intent.message}"

    def _format_unreachable(self, reachability: Dict) -> str:
        """格式化不可达信息 (诚实告知)"""
        lines = [f"抱歉，{reachability.get('reason', '无法联系目标')}"]

        suggestions = reachability.get("suggestions", [])
        if suggestions:
            lines.append("\n建议方案：")
            for i, s in enumerate(suggestions, 1):
                lines.append(f"  {i}. {s}")

        return "\n".join(lines)

    def _log_message(self, intent: CommIntent, method: Dict, formatted_msg: str):
        """记录消息日志"""
        self.message_log.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "intent": asdict(intent),
            "method": method.get("method", ""),
            "message": formatted_msg,
        })

    # ==================== 关系管理快捷方法 ====================

    def add_bot(self, bot_username: str, bot_name: str, owner_name: str,
                groups: List[str] = None, channels: List[str] = None,
                is_admin: bool = False, privacy_mode: bool = False) -> bool:
        """添加 Bot 关系"""
        relation = BotRelation(
            owner_id=owner_name,
            owner_name=owner_name,
            bot_username=bot_username,
            bot_name=bot_name,
            groups=groups or [],
            channels=channels or [],
            is_admin=is_admin,
            privacy_mode=privacy_mode,
            last_seen=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        return self.relations.add_relation(relation)

    def remove_bot(self, bot_username: str) -> bool:
        """移除 Bot 关系"""
        return self.relations.remove_relation(bot_username)

    def list_bots(self) -> List[Dict]:
        """列出所有已知 Bot"""
        return self.relations.list_all()

    def check_bot(self, target: str) -> Dict:
        """检查目标 Bot 的可达性"""
        return self.relations.check_reachability(target)

    def scan_groups(self, group_list: List[Dict]) -> int:
        """扫描群组列表，自动构建关系表

        参数:
            group_list: [{"group_id": "...", "members": [{"username": "...", "name": "...", "is_bot": True}]}]

        返回:
            新发现的 Bot 数量
        """
        found = 0
        for group in group_list:
            group_id = group.get("group_id", "")
            for member in group.get("members", []):
                if member.get("is_bot"):
                    username = member.get("username", "")
                    name = member.get("name", username)
                    existing = self.relations.find_bot(username)
                    if existing:
                        if group_id not in existing.groups:
                            existing.groups.append(group_id)
                    else:
                        relation = BotRelation(
                            owner_id="",
                            owner_name="未知",
                            bot_username=f"@{username.lstrip('@')}",
                            bot_name=name,
                            groups=[group_id],
                        )
                        self.relations.relations.append(relation)
                        found += 1
        if found > 0:
            self.relations.save()
        return found

    # ==================== 状态 ====================

    def status(self) -> Dict:
        """获取系统状态"""
        return {
            "total_bots": len(self.relations.relations),
            "total_messages_sent": len(self.message_log),
            "bots": [
                {
                    "name": r.bot_name,
                    "username": r.bot_username,
                    "owner": r.owner_name,
                    "groups": len(r.groups),
                    "channels": len(r.channels),
                    "admin": r.is_admin,
                    "privacy": r.privacy_mode,
                }
                for r in self.relations.relations
            ],
        }
