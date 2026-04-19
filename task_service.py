from config import Config

_tasks = [
    {"id": 1, "title": "Review Q2 report", "status": "done"},
    {"id": 2, "title": "Update API docs", "status": "done"},
    {"id": 3, "title": "Fix login bug", "status": "prog"},
    {"id": 4, "title": "Design new dashboard", "status": "prog"},
    {"id": 5, "title": "Write unit tests", "status": "todo"},
]
_next_id = 6

def get_tasks():
    return _tasks

def add_task(title: str) -> dict:
    global _next_id
    task = {"id": _next_id, "title": title, "status": "todo"}
    _tasks.append(task)
    _next_id += 1
    return {"status": "success", "task": task}

def update_task_status(task_id: int, status: str) -> dict:
    for t in _tasks:
        if t["id"] == task_id:
            t["status"] = status
            return {"status": "success", "task": t}
    return {"status": "error", "message": "Task not found"}
