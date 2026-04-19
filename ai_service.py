import json
import dateparser
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

# ─── Intent Classification ────────────────────────────────────────────────────

def parse_intent(message: str) -> dict:
    """
    Analyzes message and extracts structured JSON.
    Supports: Task, Schedule, Plan, Query, Reminder, Note, Weather, Math, Translate, Summarize
    """

    prompt = f"""
You are an intelligent intent classifier. Analyze the user's message and return structured JSON.

Valid intents:
- "Task"      → action to do / todo item
- "Schedule"  → calendar event with a time/date
- "Plan"      → generate a step-by-step plan or roadmap
- "Query"     → general question or information request
- "Reminder"  → remind me at a certain time
- "Note"      → save a note or idea
- "Weather"   → weather-related query
- "Math"      → calculation or math problem
- "Translate" → language translation request
- "Summarize" → summarize text or a topic

Extract ALL relevant fields from this list:
- intent (string, required)
- title (string, required — exact words, no abbreviation or summarization)
- description (string, optional — extra context)
- priority (string: "high", "medium", "low" — ONLY for Task/Reminder)
- raw_date_string (string — ONLY for Schedule/Reminder, exact words user used like "next friday at 5pm")
- tags (array of strings — relevant labels, e.g. ["work", "urgent"])
- target_language (string — ONLY for Translate, e.g. "French")
- text_to_process (string — ONLY for Summarize/Translate, the actual content)
- math_expression (string — ONLY for Math, the expression to evaluate)

User message: "{message}"

Return ONLY valid JSON. No extra text.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    intent_data = json.loads(response.choices[0].message.content)
    intent = intent_data.get("intent", "Query")

    # ── Date parsing for Schedule / Reminder ──────────────────────────────────
    if intent in ("Schedule", "Reminder"):
        raw_date = intent_data.pop("raw_date_string", "") or ""
        parsed_time = dateparser.parse(raw_date, settings={"PREFER_DATES_FROM": "future"})
        intent_data["datetime"] = parsed_time.isoformat() if parsed_time else "TBD"

    # ── Inline math evaluation (safe, no exec) ────────────────────────────────
    if intent == "Math":
        expr = intent_data.get("math_expression", "")
        intent_data["result"] = _safe_eval(expr)

    return intent_data


# ─── Feature Handlers ─────────────────────────────────────────────────────────

def generate_plan(title: str, description: str = "") -> dict:
    """Generates a detailed, structured step-by-step plan."""
    prompt = f"""
Create a clear, detailed, numbered step-by-step action plan for:
Title: {title}
Details: {description or "none provided"}

Format each step as:
1. [Step title]: [Brief explanation]

Also include:
- Estimated total time
- Key resources needed
- Potential blockers to watch out for
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content
    steps = [s.strip() for s in raw.split("\n") if s.strip()]
    return {"title": title, "plan_steps": steps, "raw": raw}


def handle_query(title: str, description: str = "") -> dict:
    """Answers any general question with a well-structured response."""
    prompt = f"""
You are a helpful, knowledgeable AI assistant. Answer the following clearly and concisely.
If it's factual, be accurate. If it's opinion-based, be balanced.

Question: {title}
Context: {description or "none"}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful, precise AI assistant. Keep answers concise but complete."},
            {"role": "user", "content": prompt}
        ]
    )
    return {"query": title, "answer": response.choices[0].message.content}


def summarize_text(text: str, title: str = "") -> dict:
    """Summarizes any given text or topic."""
    is_topic = len(text.split()) < 10  # short = treat as topic, not raw text
    if is_topic:
        prompt = f"Give a clear, concise summary of the topic: {text}"
    else:
        prompt = f"Summarize the following text in 3-5 sentences, capturing the key points:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"title": title or "Summary", "summary": response.choices[0].message.content}


def translate_text(text: str, target_language: str, title: str = "") -> dict:
    """Translates text to any target language."""
    prompt = f"Translate the following to {target_language}. Return only the translation:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "original": text,
        "target_language": target_language,
        "translation": response.choices[0].message.content
    }


def handle_weather_query(title: str) -> dict:
    """Handles weather queries — extracts location and advises user."""
    prompt = f"""
The user asked: "{title}"
Extract the location they're asking about. If no location, say "unspecified".
Then reply helpfully, noting that you don't have real-time data and suggesting they check a weather service.
Return JSON: {{ "location": "...", "answer": "..." }}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)


def handle_note(title: str, description: str = "") -> dict:
    """Structures and stores a note with suggested tags."""
    prompt = f"""
A user wants to save a note. Clean it up and suggest 2-3 relevant tags.
Title: {title}
Body: {description or "none"}
Return JSON: {{ "title": "...", "body": "...", "tags": ["...", "..."] }}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)


# ─── Main Router ──────────────────────────────────────────────────────────────

def process_message(message: str) -> dict:
    """
    Main entry point. Parses intent then routes to correct handler.
    Returns a unified response dict with 'intent', 'reply', 'action', 'data'.
    """
    try:
        intent_data = parse_intent(message)
        intent = intent_data.get("intent", "Query")
        title = intent_data.get("title", message)
        description = intent_data.get("description", "")

        if intent == "Task":
            return {
                "intent": "Task",
                "reply": f"Task created: **{title}**" + (f" (Priority: {intent_data.get('priority','medium')})" if intent_data.get('priority') else ""),
                "action": "add_task",
                "data": intent_data
            }

        elif intent == "Schedule":
            dt = intent_data.get("datetime", "TBD")
            return {
                "intent": "Schedule",
                "reply": f"Event scheduled: **{title}** at `{dt}`",
                "action": "add_event",
                "data": intent_data
            }

        elif intent == "Reminder":
            dt = intent_data.get("datetime", "TBD")
            return {
                "intent": "Reminder",
                "reply": f"Reminder set: **{title}** at `{dt}`",
                "action": "add_reminder",
                "data": intent_data
            }

        elif intent == "Plan":
            result = generate_plan(title, description)
            return {
                "intent": "Plan",
                "reply": result["raw"],
                "action": "show_plan",
                "data": result
            }

        elif intent == "Summarize":
            text = intent_data.get("text_to_process", title)
            result = summarize_text(text, title)
            return {
                "intent": "Summarize",
                "reply": result["summary"],
                "action": "show_summary",
                "data": result
            }

        elif intent == "Translate":
            text = intent_data.get("text_to_process", title)
            lang = intent_data.get("target_language", "English")
            result = translate_text(text, lang, title)
            return {
                "intent": "Translate",
                "reply": f"**{lang}:** {result['translation']}",
                "action": "show_translation",
                "data": result
            }

        elif intent == "Math":
            result = intent_data.get("result", "Could not evaluate")
            return {
                "intent": "Math",
                "reply": f"`{intent_data.get('math_expression', '')}` = **{result}**",
                "action": "show_result",
                "data": intent_data
            }

        elif intent == "Weather":
            result = handle_weather_query(title)
            return {
                "intent": "Weather",
                "reply": result.get("answer", "I can't fetch real-time weather, please check a weather service."),
                "action": "show_weather",
                "data": result
            }

        elif intent == "Note":
            result = handle_note(title, description)
            return {
                "intent": "Note",
                "reply": f"Note saved: **{result.get('title', title)}**",
                "action": "save_note",
                "data": result
            }

        else:  # Query fallback
            result = handle_query(title, description)
            return {
                "intent": "Query",
                "reply": result["answer"],
                "action": "show_answer",
                "data": result
            }

    except Exception as e:
        return {
            "intent": "Error",
            "reply": f"Something went wrong: {str(e)}",
            "action": None,
            "data": {}
        }


# ─── Safe Math Evaluator ──────────────────────────────────────────────────────

def _safe_eval(expression: str):
    """Evaluates basic math expressions safely without exec/eval."""
    import ast, operator
    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg,
        ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv
    }
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        else:
            raise ValueError("Unsupported expression")
    try:
        tree = ast.parse(expression, mode='eval')
        result = _eval(tree.body)
        return round(result, 10) if isinstance(result, float) else result
    except Exception:
        return "Could not evaluate"