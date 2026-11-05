import tempfile
import unittest
from pathlib import Path

from pocketpilot.agent import Agent
from pocketpilot.model import DemoModel
from pocketpilot.store import Store


class AgentTests(unittest.TestCase):
    def test_task_and_memory_survive_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "data.db")
            agent = Agent(Store(path), DemoModel())
            self.assertIn("已添加", agent.ask("添加待办 买牛奶"))
            self.assertIn("已记住", agent.ask("记住 我喜欢咖啡"))
            fresh = Agent(Store(path), DemoModel())
            self.assertIn("买牛奶", fresh.ask("查看待办"))
            self.assertIn("咖啡", fresh.ask("回忆 咖啡"))

    def test_tool_allowlist_and_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = Agent(Store(str(Path(tmp) / "data.db")), DemoModel())
            with self.assertRaises(ValueError):
                agent.run_tool("run_shell", {"command": "echo hi"})
            with self.assertRaises(ValueError):
                agent.run_tool("forget", {"memory_id": "1"})


if __name__ == "__main__":
    unittest.main()
