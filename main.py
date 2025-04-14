from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
import requests
import os
import random
from fastapi.staticfiles import StaticFiles
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
TICKETMASTER_URL = os.getenv("TICKETMASTER_URL")

def get_events(city: str = "New York", event_type: str = "music"):
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city,
        "classificationName": event_type,
        "size": 10
    }
    response = requests.get(TICKETMASTER_URL, params=params)
    data = response.json()
    print(f"[Ticketmaster] URL: {response.url}")
    print(f"[Ticketmaster] Status Code: {response.status_code}")
    print(f"[Ticketmaster] Snippet: {response.text[:300]}")
    return data.get("_embedded", {}).get("events", [])

# Location API
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, city: str = None, event_type: str = "music"):
    # Detect city if not provided
    if not city:
        try:
            geo = requests.get("https://ipinfo.io/json").json()
            city = geo.get("city", "New York")
            print(f"[Geo] Auto-detected city: {city}")
        except Exception as e:
            print("[Geo] Failed to get location:", e)
            city = "New York"

    events = get_events(city, event_type)

    cat_url = None
    if not events:
        cat_url = "https://cataas.com/cat/says/No%20events%20found!"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "city": city,
        "event_type": event_type,
        "events": events,
        "cat_url": cat_url
    })

@app.get("/random", response_class=HTMLResponse)
async def random_concert(request: Request):
    events = get_events()
    if not events:
        return templates.TemplateResponse("random.html", {"request": request, "event": None})
    
    event = random.choice(events)
    return templates.TemplateResponse("random.html", {"request": request, "event": event})
