import json
import dateparser
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def parse_intent(message: str) -> dict:
    """Step 2 & 3: Analyzes message and extracts structured JSON data."""
    
    prompt = f"""
    Analyze the following user message and extract the intent.
    Valid intents are: "Task", "Schedule", "Plan", "Query".
    
    Extract the following fields:
    - intent (string)
    - title (string - IMPORTANT: Do NOT abbreviate, do NOT summarize, and do NOT misspell. Use the exact subject words from the user's message.)
    - description (string, optional)
    - priority (string: "high", "medium", "low" - ONLY if intent is Task)
    - raw_date_string (string - ONLY if intent is Schedule. Extract EXACTLY the words the user used to describe the time. E.g., "next friday at 5pm" or "christmas". DO NOT try to calculate or convert it to a JSON date.)
    
    Message: "{message}"
    
    Return ONLY valid JSON.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )
    
    intent_data = json.loads(response.choices[0].message.content)
    
    # If it's a schedule, use dateparser to convert the raw words into a strict ISO format
    if intent_data.get("intent") == "Schedule":
        raw_date = intent_data.get("raw_date_string", "")
        
        # dateparser handles "christmas", "tomorrow", "in 3 days", etc. perfectly
        parsed_time = dateparser.parse(
            raw_date, 
            settings={'PREFER_DATES_FROM': 'future'}
        )
        
        if parsed_time:
            # Converts "christmas" into "2024-12-25T00:00:00"
            intent_data['datetime'] = parsed_time.isoformat()
        else:
            intent_data['datetime'] = "TBD" # Fallback only if completely unrecognizable
            
        # Remove the raw string so the frontend doesn't get confused
        del intent_data['raw_date_string']
        
    return intent_data

def generate_plan(title: str, description: str) -> dict:
    """Step 5C: Generates a detailed step-by-step plan using AI."""
    prompt = f"Create a detailed, step-by-step action plan for: {title}. Details: {description}"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "title": title,
        "plan_steps": response.choices[0].message.content.split('\n')
    }

def handle_query(title: str, description: str) -> dict:
    """Step 5D: Responds to general queries."""
    prompt = f"You are an AI assistant. Answer the following query concisely: {title} {description}"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "query": title,
        "answer": response.choices[0].message.content
    }