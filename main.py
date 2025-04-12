from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
import requests
import os
import random

load_dotenv()

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, city: str = "New York", event_type: str = "music"):
    events = get_events(city, event_type)

    cat_url = None
    if not events:
        # fallback cat image with text
        cat_url = "https://cataas.com/cat/says/No%20concerts%20found!"

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
