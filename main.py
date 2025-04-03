from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

# Configure Jinja2 template directory
templates = Jinja2Templates(directory="templates")

# Your Ticketmaster API Key
TICKETMASTER_API_KEY = "jiAu09QH4Ezgh7rdBNv0kYjTK7RY59OA"
TICKETMASTER_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

# Function to fetch events from Ticketmaster API based on the city
def get_events(city: str = "New York", event_type: str = "music"):
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city,
        "classificationName": event_type,  # You can also filter by event type like "music"
        "size": 10  # Number of events to fetch
    }
    response = requests.get(TICKETMASTER_URL, params=params)
    data = response.json()

    # Extract events if available
    return data.get("_embedded", {}).get("events", [])

# FastAPI Route to Render the Home Page with a form to select city and event type
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, city: str = "New York", event_type: str = "music"):
    events = get_events(city, event_type)
    return templates.TemplateResponse("index.html", {"request": request, "city": city, "event_type": event_type, "events": events})

