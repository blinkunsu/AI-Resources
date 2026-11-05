import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Store:
    def __init__(self, path: str = "pocketpilot.db"):
        self.path = str(Path(path))
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY, content TEXT NOT NULL
                );
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def add_task(self, title: str) -> str:
        with self.connect() as db:
            cur = db.execute("INSERT INTO tasks(title) VALUES (?)", (title,))
            return f"已添加待办 #{cur.lastrowid}：{title}"

    def list_tasks(self) -> str:
        with self.connect() as db:
            rows = db.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return "\n".join(f"#{i} {'✓' if done else '○'} {title}" for i, title, done in rows) or "暂无待办。"

    def complete_task(self, task_id: int) -> str:
        with self.connect() as db:
            cur = db.execute("UPDATE tasks SET done=1 WHERE id=? AND done=0", (task_id,))
            return f"已完成待办 #{task_id}。" if cur.rowcount else "没有找到未完成的该编号待办。"

    def remember(self, content: str) -> str:
        with self.connect() as db:
            cur = db.execute("INSERT INTO memories(content) VALUES (?)", (content,))
            return f"已记住 #{cur.lastrowid}：{content}"

    def recall(self, keyword: str = "") -> str:
        with self.connect() as db:
            rows = db.execute("SELECT id, content FROM memories ORDER BY id").fetchall()
        rows = [(i, text) for i, text in rows if keyword.casefold() in text.casefold()]
        return "\n".join(f"#{i} {text}" for i, text in rows) or "没有找到记忆。"

    def forget(self, memory_id: int) -> str:
        with self.connect() as db:
            cur = db.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            return f"已删除记忆 #{memory_id}。" if cur.rowcount else "没有找到该编号记忆。"
