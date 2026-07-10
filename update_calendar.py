import re
from datetime import datetime, timedelta, timezone

import requests
from icalendar import Calendar, Event


SHOWS = {
    1453: "Big Brother",
    84768: "Big Brother Unlocked",
}

EPISODE_LENGTH = timedelta(hours=1)

# Only keep episodes from the last N days onward (plus all future episodes)
LOOKBACK_DAYS = 30


cal = Calendar()
cal.add("prodid", "-//Big Brother Calendar//")
cal.add("version", "2.0")

now_utc = datetime.now(timezone.utc)
cutoff = now_utc - timedelta(days=LOOKBACK_DAYS)


def strip_html(text: str) -> str:
    """TVMaze summaries come as HTML - strip tags for a plain-text description."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


events_added = 0

for show_id, show_name in SHOWS.items():
    url = f"https://api.tvmaze.com/shows/{show_id}/episodes"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    episodes = response.json()

    for ep in episodes:
        if not ep.get("airstamp"):
            continue

        start = datetime.fromisoformat(
            ep["airstamp"].replace("Z", "+00:00")
        )

        if start < cutoff:
            continue

        event = Event()

        event.add(
            "uid",
            f'tvmaze-{show_id}-ep-{ep["id"]}@bigbrother-calendar'
        )

        event.add("dtstamp", now_utc)

        event.add(
            "summary",
            f'{show_name} S{ep["season"]:02d}E{ep["number"]:02d}'
        )

        event.add("dtstart", start)
        event.add("dtend", start + EPISODE_LENGTH)

        description = strip_html(ep.get("summary", ""))

        if description:
            event.add("description", description)

        cal.add_component(event)
        events_added += 1


with open("bigbrother.ics", "wb") as f:
    f.write(cal.to_ical())


print(f"Calendar updated with {events_added} events.")
