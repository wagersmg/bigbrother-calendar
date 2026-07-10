import re
from datetime import datetime, timedelta, timezone

import requests
from icalendar import Calendar, Event

SHOW_ID = 1453  # TVMaze Big Brother (US)
EPISODE_LENGTH = timedelta(hours=1)

# Set to False if you only want current/upcoming episodes instead of full history
INCLUDE_PAST_EPISODES = True

url = f"https://api.tvmaze.com/shows/{SHOW_ID}/episodes"
episodes = requests.get(url, timeout=30).json()

cal = Calendar()
cal.add("prodid", "-//Big Brother Calendar//")
cal.add("version", "2.0")

now_utc = datetime.now(timezone.utc)

def strip_html(text: str) -> str:
    """TVMaze summaries come as HTML - strip tags for a plain-text description."""
    return re.sub(r"<[^>]+>", "", text or "").strip()

for ep in episodes:
    if not ep.get("airstamp"):
        continue

    start = datetime.fromisoformat(ep["airstamp"].replace("Z", "+00:00"))

    if not INCLUDE_PAST_EPISODES and start < now_utc:
        continue

    event = Event()

    event.add("uid", f'tvmaze-ep-{ep["id"]}@bigbrother-calendar')
    event.add("dtstamp", now_utc)
    event.add("summary", f'Big Brother - {ep["name"]}')
    event.add("dtstart", start)
    event.add("dtend", start + EPISODE_LENGTH)
    event.add("description", strip_html(ep.get("summary", "")))

    cal.add_component(event)

with open("bigbrother.ics", "wb") as f:
    f.write(cal.to_ical())

print(f"Calendar updated with {len(cal.subcomponents)} events.")
