# AI Planner

AI-powered calendar and task manager with Flask backend + HTML frontend.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## .env Configuration

```
GOOGLE_CALENDAR_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
SECRET_KEY=your_secret_here
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | /ai | Send message to AI assistant |
| GET | /tasks | List all tasks |
| POST | /tasks | Create a task |
| PATCH | /tasks/<id> | Update task status |
| GET | /calendar/events | List events |
| POST | /calendar/events | Add calendar event |

## Project Structure

```
ai-planner/
├── app.py               # Flask app + routes
├── ai_service.py        # AI message processing
├── calendar_service.py  # Google Calendar integration
├── task_service.py      # Task CRUD
├── config.py            # Environment config
├── requirements.txt
├── .env                 # API keys (never commit this)
└── frontend/
    └── index.html       # Full UI (served by Flask on /)
```
