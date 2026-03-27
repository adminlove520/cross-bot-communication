"""
Cross-Bot Communication - 跨 Bot 通信的智能解决方案
让龙虾等 AI 助手能够通过 Telegram 群/频道实现跨 Bot 消息传递
"""

from .bot_comm import BotCommunicator
from .intent_parser import IntentParser
from .relation_manager import RelationManager

__all__ = ["BotCommunicator", "IntentParser", "RelationManager"]
