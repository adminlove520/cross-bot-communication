"""
意图解析器 - 从用户消息中提取通信意图
"""

import re
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class CommIntent:
    """通信意图"""
    action: str          # "contact", "notify", "ask", "relay", "unknown"
    target: str          # 目标 Bot/人 标识
    message: str         # 要传递的消息内容
    urgency: str = "normal"  # "urgent", "normal", "low"
    raw_text: str = ""   # 原始文本
    confidence: float = 0.0  # 置信度 0-1


class IntentParser:
    """从自然语言中解析跨 Bot 通信意图"""

    # 意图关键词映射
    CONTACT_KEYWORDS = [
        "联系", "找", "叫", "通知", "告诉", "帮忙", "传话", "转告",
        "contact", "tell", "notify", "message", "ask",
    ]

    URGENCY_KEYWORDS = {
        "urgent": ["紧急", "马上", "立刻", "赶紧", "urgent", "asap", "immediately"],
        "low": ["有空", "方便时", "不急", "when free", "low priority"],
    }

    # Bot 名称识别模式
    AT_PATTERN = re.compile(r"@(\w+)")
    BOT_NAME_PATTERN = re.compile(r"(小\w+|龙虾|[\w]+[Bb]ot)")

    def parse(self, text: str) -> CommIntent:
        """解析消息文本，提取通信意图"""
        text = text.strip()
        if not text:
            return CommIntent(action="unknown", target="", message="", raw_text=text)

        # 1. 识别目标
        target = self._extract_target(text)

        # 2. 识别动作
        action, confidence = self._detect_action(text)

        # 3. 提取消息内容
        message = self._extract_message(text, target)

        # 4. 检测紧急程度
        urgency = self._detect_urgency(text)

        return CommIntent(
            action=action,
            target=target,
            message=message,
            urgency=urgency,
            raw_text=text,
            confidence=confidence,
        )

    def _extract_target(self, text: str) -> str:
        """提取目标 Bot/人"""
        # 优先匹配 @username
        at_match = self.AT_PATTERN.search(text)
        if at_match:
            return f"@{at_match.group(1)}"

        # 匹配中文 Bot 名称 (如"小敏"、"小隐")
        name_match = self.BOT_NAME_PATTERN.search(text)
        if name_match:
            return name_match.group(1)

        # 尝试从动词后提取目标
        for kw in ["联系", "找", "叫", "通知", "告诉"]:
            if kw in text:
                idx = text.index(kw) + len(kw)
                remaining = text[idx:].strip()
                # 取到逗号或句号
                for sep in ["，", ",", "。", "，", " ", "让", "说"]:
                    if sep in remaining:
                        return remaining[:remaining.index(sep)].strip()
                if len(remaining) <= 10:
                    return remaining.strip()

        return ""

    def _detect_action(self, text: str) -> tuple:
        """检测动作类型和置信度"""
        text_lower = text.lower()

        # 联系/通知 类
        contact_score = sum(1 for kw in self.CONTACT_KEYWORDS if kw in text_lower)
        if contact_score > 0:
            confidence = min(0.5 + contact_score * 0.2, 1.0)
            # 细分动作
            if any(kw in text_lower for kw in ["通知", "告诉", "notify", "tell"]):
                return "notify", confidence
            if any(kw in text_lower for kw in ["问", "ask", "请教"]):
                return "ask", confidence
            return "contact", confidence

        # @提及
        if "@" in text:
            return "contact", 0.6

        return "unknown", 0.0

    def _extract_message(self, text: str, target: str) -> str:
        """从文本中提取要传递的消息"""
        # 移除目标名称和动作关键词，剩下的就是消息内容
        msg = text
        if target:
            msg = msg.replace(target, "").strip()

        # 移除常见的动作词前缀
        for prefix in ["联系", "找", "叫", "通知", "告诉", "帮忙", "让", "说"]:
            if msg.startswith(prefix):
                msg = msg[len(prefix):].strip()

        # 清理
        msg = msg.strip("，,。.！! ")
        return msg if msg else text

    def _detect_urgency(self, text: str) -> str:
        """检测紧急程度"""
        text_lower = text.lower()
        for level, keywords in self.URGENCY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return level
        return "normal"

    def is_cross_bot_intent(self, text: str) -> bool:
        """快速判断是否包含跨 Bot 通信意图"""
        intent = self.parse(text)
        return intent.action != "unknown" and intent.target != "" and intent.confidence > 0.3
