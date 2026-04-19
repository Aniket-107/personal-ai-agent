from config import Config
import re

def process_ai_message(message: str) -> dict:
    """Processes user message and routes to appropriate service."""
    lower = message.lower()

    if any(w in lower for w in ['add', 'schedule', 'meeting', 'event', 'calendar']):
        time_match = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm)?)', message, re.IGNORECASE)
        day_match = re.search(r'(today|tomorrow|monday|tuesday|wednesday|thursday|friday)', message, re.IGNORECASE)
        day = day_match.group(0) if day_match else 'soon'
        time = time_match.group(0) if time_match else 'TBD'
        title = re.sub(r'add|schedule|create|an|a|event|meeting|at|tomorrow|today|\d{1,2}(:\d{2})?\s*(am|pm)?', '', message, flags=re.IGNORECASE).strip() or 'New Meeting'
        return {
            "intent": "calendar",
            "reply": f"Event added: {title} on {day} at {time}.",
            "action": "add_event",
            "data": {"title": title, "event_time": f"{day} {time}"}
        }

    elif any(w in lower for w in ['task', 'todo', 'remind', 'create']):
        title = re.sub(r'add|create|task|to.?do|remind me to', '', message, flags=re.IGNORECASE).strip() or 'New Task'
        return {
            "intent": "task",
            "reply": f"Task added: {title}",
            "action": "add_task",
            "data": {"title": title}
        }

    elif any(w in lower for w in ['list', 'show', 'what']):
        return {
            "intent": "query",
            "reply": "Fetching your current tasks and events.",
            "action": "list"
        }

    return {
        "intent": "unknown",
        "reply": "I can help you schedule events or manage tasks. Try: 'Add a meeting at 3pm' or 'Create task: Review code'.",
        "action": None
    }
