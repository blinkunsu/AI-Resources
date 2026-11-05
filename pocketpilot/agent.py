from .store import Store


class Agent:
    def __init__(self, store: Store, model):
        self.store = store
        self.model = model

    def run_tool(self, name: str, args: dict) -> str:
        if not isinstance(args, dict):
            raise ValueError("工具参数必须是对象")
        if name in {"add_task", "remember"}:
            key = "title" if name == "add_task" else "content"
            value = args.get(key)
            if not isinstance(value, str) or not value.strip() or len(value) > 500:
                raise ValueError(f"{key} 需要 1 到 500 个字符")
            return getattr(self.store, name)(value.strip())
        if name == "list_tasks":
            return self.store.list_tasks()
        if name == "recall":
            value = args.get("keyword", "")
            if not isinstance(value, str) or len(value) > 100:
                raise ValueError("keyword 无效")
            return self.store.recall(value)
        if name in {"complete_task", "forget"}:
            key = "task_id" if name == "complete_task" else "memory_id"
            value = args.get(key)
            if type(value) is not int or value < 1:
                raise ValueError(f"{key} 必须是正整数")
            return getattr(self.store, name)(value)
        raise ValueError("工具不在允许列表中")

    def ask(self, text: str) -> str:
        messages = [{"role": "user", "content": text}]
        for _ in range(3):
            action = self.model.propose(messages)
            if not isinstance(action, dict):
                raise ValueError("模型没有返回 JSON 对象")
            if "answer" in action:
                return str(action["answer"])
            name = action.get("tool")
            result = self.run_tool(name, action.get("arguments", {}))
            messages.append({"role": "assistant", "content": str(action)})
            messages.append({"role": "tool", "content": result})
        return "操作步数达到上限，请拆分请求。"
