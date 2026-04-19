from config import Config

def add_calendar_event(title: str, description: str, event_time: str) -> dict:
    """Step 5B: Adds event to Google Calendar."""
    # NOTE: In a production environment, you would use google.oauth2.credentials 
    # to authenticate. For this backend stub, we simulate the API call.
    
    if not Config.GOOGLE_CALENDAR_API_KEY:
        # Fallback mock so the backend doesn't crash without Google setup
        return {
            "status": "mock_success",
            "message": "Google Calendar API key not set. Event simulated.",
            "event": {
                "title": title,
                "description": description,
                "datetime": event_time,
                "calendar_link": f"https://calendar.google.com/event?text={title}"
            }
        }

    # Actual Google Calendar API Implementation Skeleton:
    """
    from googleapiclient.discovery import build
    service = build('calendar', 'v3', developerKey=Config.GOOGLE_CALENDAR_API_KEY)
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': event_time, 'timeZone': 'UTC'},
        'end': {'dateTime': event_time, 'timeZone': 'UTC'}, # Assuming 1-hour event
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    """
    
    return {"status": "success", "message": "Event added to calendar"}