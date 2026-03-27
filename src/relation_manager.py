"""
社交关系管理器 - 管理 Bot 之间的关系表
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class BotRelation:
    """Bot 关系记录"""
    owner_id: str                   # 主人标识
    owner_name: str                 # 主人名称
    bot_username: str               # Bot 的 @用户名
    bot_name: str                   # Bot 昵称
    groups: List[str] = field(default_factory=list)      # 共同群组 ID
    channels: List[str] = field(default_factory=list)    # 共同频道 ID
    is_admin: bool = False          # 是否是管理员
    privacy_mode: bool = False      # 隐私模式是否开启
    last_seen: str = ""             # 最后活跃时间
    capabilities: List[str] = field(default_factory=list)  # Bot 能力标签


class RelationManager:
    """社交关系管理器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config.json"
        )
        self.relations: List[BotRelation] = []
        self._load()

    def _load(self):
        """从配置文件加载关系表"""
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("relations", []):
                self.relations.append(BotRelation(**item))
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[WARN] 加载关系表失败: {e}")

    def save(self):
        """保存关系表到文件"""
        data = {"relations": [asdict(r) for r in self.relations]}
        os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def find_bot(self, identifier: str) -> Optional[BotRelation]:
        """查找 Bot (支持 @用户名、昵称、主人名)"""
        identifier_lower = identifier.lower().strip().lstrip("@")
        for r in self.relations:
            if (identifier_lower == r.bot_username.lower().lstrip("@")
                    or identifier_lower == r.bot_name.lower()
                    or identifier_lower == r.owner_name.lower()):
                return r
        return None

    def find_bots_in_group(self, group_id: str) -> List[BotRelation]:
        """查找同一群组中的所有 Bot"""
        return [r for r in self.relations if group_id in r.groups]

    def find_bots_in_channel(self, channel_id: str) -> List[BotRelation]:
        """查找同一频道中的所有 Bot"""
        return [r for r in self.relations if channel_id in r.channels]

    def add_relation(self, relation: BotRelation) -> bool:
        """添加或更新关系"""
        existing = self.find_bot(relation.bot_username)
        if existing:
            # 更新
            existing.groups = list(set(existing.groups + relation.groups))
            existing.channels = list(set(existing.channels + relation.channels))
            existing.is_admin = relation.is_admin or existing.is_admin
            existing.privacy_mode = relation.privacy_mode
            existing.last_seen = relation.last_seen
        else:
            self.relations.append(relation)
        self.save()
        return True

    def remove_relation(self, bot_username: str) -> bool:
        """移除关系"""
        bot_username = bot_username.lower().lstrip("@")
        before = len(self.relations)
        self.relations = [r for r in self.relations
                          if r.bot_username.lower().lstrip("@") != bot_username]
        if len(self.relations) < before:
            self.save()
            return True
        return False

    def list_all(self) -> List[Dict]:
        """列出所有关系 (JSON 序列化)"""
        return [asdict(r) for r in self.relations]

    def check_reachability(self, target_bot: str) -> Dict:
        """检查是否可以联系目标 Bot，返回可行方案"""
        bot = self.find_bot(target_bot)
        if not bot:
            return {
                "reachable": False,
                "reason": f"未找到 Bot: {target_bot}",
                "suggestions": [
                    "确认 Bot 名称是否正确",
                    "将目标 Bot 拉入同一群组或频道",
                    "手动添加关系配置",
                ],
            }

        methods = []

        # 检查群组
        if bot.groups:
            if bot.is_admin:
                methods.append({
                    "method": "group_mention",
                    "description": f"在群组中 @{bot.bot_username}",
                    "reliability": "high",
                    "groups": bot.groups,
                })
            elif not bot.privacy_mode:
                methods.append({
                    "method": "group_message",
                    "description": f"在群组中发送消息 (Privacy Mode 已关闭)",
                    "reliability": "medium",
                    "groups": bot.groups,
                })

        # 检查频道
        if bot.channels:
            methods.append({
                "method": "channel_relay",
                "description": f"通过频道中转消息",
                "reliability": "medium",
                "channels": bot.channels,
            })

        if not methods:
            suggestions = []
            if bot.privacy_mode:
                suggestions.append(f"关闭 {bot.bot_name} 的 Privacy Mode")
            if not bot.is_admin:
                suggestions.append(f"将 {bot.bot_name} 设为群管理员")
            if not bot.groups and not bot.channels:
                suggestions.append("将两个 Bot 拉入同一群组")

            return {
                "reachable": False,
                "reason": "没有可用的通信方式",
                "bot": asdict(bot),
                "suggestions": suggestions,
            }

        return {
            "reachable": True,
            "bot": asdict(bot),
            "methods": methods,
            "recommended": methods[0],
        }
