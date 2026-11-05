import argparse
import os

from .agent import Agent
from .model import CompatibleModel, DemoModel
from .store import Store


def main():
    parser = argparse.ArgumentParser(description="PocketPilot 个人智能体")
    parser.add_argument("mode", nargs="?", choices=["demo", "chat"], default="demo")
    parser.add_argument("--db", default="pocketpilot.db", help="本地数据库路径")
    args = parser.parse_args()
    if args.mode == "chat" and not all(os.getenv(k) for k in ("MODEL_BASE_URL", "MODEL_API_KEY", "MODEL_NAME")):
        parser.error("chat 模式需要 MODEL_BASE_URL、MODEL_API_KEY 和 MODEL_NAME")
    agent = Agent(Store(args.db), CompatibleModel() if args.mode == "chat" else DemoModel())
    print("PocketPilot | 输入 /quit 退出 | 数据保存在", args.db)
    if args.mode == "demo":
        print("离线演示可输入：添加待办 买牛奶 / 查看待办 / 记住 我喜欢咖啡 / 回忆 咖啡")
    while True:
        try:
            text = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见")
            break
        if text in {"/quit", "/exit"}:
            break
        if not text:
            continue
        try:
            print("助手>", agent.ask(text))
        except Exception as exc:
            print("操作失败：", exc)


if __name__ == "__main__":
    main()
