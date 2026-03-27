#!/usr/bin/env python3
"""
Cross-Bot Communication CLI - 跨 Bot 通信命令行工具
方便龙虾和其他 AI 助手直接调用
"""

import argparse
import json
import sys
from src.bot_comm import BotCommunicator


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Bot Communication - 跨 Bot 通信工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py send "联系小敏，让它主人明天开会"
  python main.py check 小敏
  python main.py list
  python main.py status
  python main.py add --username @new_bot --name 小新 --owner 主人名
  python main.py scan
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # send - 发送消息
    send_p = subparsers.add_parser("send", help="发送跨 Bot 消息")
    send_p.add_argument("message", help="消息内容 (自然语言)")
    send_p.add_argument("--json", action="store_true", help="JSON 输出")

    # check - 检查可达性
    check_p = subparsers.add_parser("check", help="检查 Bot 可达性")
    check_p.add_argument("target", help="目标 Bot (名称或 @username)")
    check_p.add_argument("--json", action="store_true", help="JSON 输出")

    # list - 列出 Bot
    list_p = subparsers.add_parser("list", help="列出所有已知 Bot")
    list_p.add_argument("--json", action="store_true", help="JSON 输出")

    # status - 系统状态
    status_p = subparsers.add_parser("status", help="系统状态")
    status_p.add_argument("--json", action="store_true", help="JSON 输出")

    # add - 添加 Bot
    add_p = subparsers.add_parser("add", help="添加 Bot 关系")
    add_p.add_argument("--username", required=True, help="Bot @username")
    add_p.add_argument("--name", required=True, help="Bot 昵称")
    add_p.add_argument("--owner", required=True, help="主人名称")
    add_p.add_argument("--groups", nargs="*", default=[], help="群组 ID")
    add_p.add_argument("--channels", nargs="*", default=[], help="频道 ID")
    add_p.add_argument("--admin", action="store_true", help="是否管理员")

    # remove - 移除 Bot
    remove_p = subparsers.add_parser("remove", help="移除 Bot")
    remove_p.add_argument("username", help="Bot @username")

    # parse - 解析意图 (调试用)
    parse_p = subparsers.add_parser("parse", help="解析消息意图 (调试)")
    parse_p.add_argument("text", help="消息文本")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    comm = BotCommunicator()
    use_json = getattr(args, "json", False)

    if args.command == "send":
        result = comm.process_message(args.message)
        if use_json:
            print(result.to_json())
        else:
            icon = "✓" if result.success else "✗"
            print(f"{icon} {result.message}")
            if result.sent_message:
                print(f"  消息: {result.sent_message}")

    elif args.command == "check":
        info = comm.check_bot(args.target)
        if use_json:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            if info["reachable"]:
                bot = info["bot"]
                method = info["recommended"]
                print(f"✓ {bot['bot_name']} (@{bot['bot_username'].lstrip('@')}) 可达")
                print(f"  推荐方式: {method['description']}")
            else:
                print(f"✗ {info['reason']}")
                for s in info.get("suggestions", []):
                    print(f"  建议: {s}")

    elif args.command == "list":
        bots = comm.list_bots()
        if use_json:
            print(json.dumps(bots, ensure_ascii=False, indent=2))
        else:
            if not bots:
                print("暂无已知 Bot")
            for b in bots:
                admin = " [管理员]" if b.get("is_admin") else ""
                privacy = " [隐私模式]" if b.get("privacy_mode") else ""
                print(f"  {b['bot_name']} (@{b['bot_username'].lstrip('@')}) "
                      f"- 主人: {b['owner_name']}{admin}{privacy}")

    elif args.command == "status":
        status = comm.status()
        if use_json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(f"已知 Bot: {status['total_bots']}")
            print(f"已发消息: {status['total_messages_sent']}")
            for b in status["bots"]:
                print(f"  {b['name']} - {b['username']} (主人: {b['owner']})")

    elif args.command == "add":
        ok = comm.add_bot(
            bot_username=args.username,
            bot_name=args.name,
            owner_name=args.owner,
            groups=args.groups,
            channels=args.channels,
            is_admin=args.admin,
        )
        print(f"{'✓' if ok else '✗'} {'已添加' if ok else '添加失败'} {args.name} ({args.username})")

    elif args.command == "remove":
        ok = comm.remove_bot(args.username)
        print(f"{'✓' if ok else '✗'} {'已移除' if ok else '未找到'} {args.username}")

    elif args.command == "parse":
        from src.intent_parser import IntentParser
        from dataclasses import asdict
        parser_inst = IntentParser()
        intent = parser_inst.parse(args.text)
        print(json.dumps(asdict(intent), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
