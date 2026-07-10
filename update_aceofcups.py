import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event


URL = "https://aceofcupsbar.com/"

CALENDAR_NAME = "Ace of Cups"
OUTPUT_FILE = "aceofcups.ics"

LOCATION = "Ace of Cups, 2619 N High St, Columbus, OH"

LOOKBACK_DAYS = 1


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def parse_event_date(date_text):
    """
    Attempts to parse common event date formats.
    Ace of Cups pages commonly use formats like:
    July 10, 2026
    Fri Jul 10
    """
    formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%A %B %d, %Y",
        "%a %b %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_text.strip(), fmt)
        except ValueError:
            pass

    return None


cal = Calendar()
cal.add("prodid", "-//Ace of Cups Calendar//")
cal.add("version", "2.0")
cal.add("X-WR-CALNAME", CALENDAR_NAME)


response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30,
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")


events_found = 0

# WordPress event pages usually expose events in article blocks.
# This intentionally searches broadly so minor site redesigns don't break it.
for item in soup.find_all(["article", "div", "section"]):

    text = clean_text(item.get_text(" ", strip=True))

    if "Ace of Cups" in text:
        continue

    if len(text) < 10:
        continue


    # Find possible dates
    date_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},\s+\d{4}",
        text,
    )

    if not date_match:
        continue


    start = parse_event_date(date_match.group(0))

    if not start:
        continue


    title = text.split(date_match.group(0))[0].strip()

    if not title:
        continue


    event = Event()

    uid = re.sub(
        r"[^a-zA-Z0-9]",
        "",
        title.lower()
    )

    event.add(
        "uid",
        f"aceofcups-{uid}@bigbrother-calendar"
    )

    event.add(
        "dtstamp",
        datetime.now(timezone.utc)
    )

    event.add(
        "summary",
        f"Ace of Cups - {title}"
    )

    event.add(
        "dtstart",
        start
    )

    event.add(
        "dtend",
        start + timedelta(hours=3)
    )

    event.add(
        "location",
        LOCATION
    )

    event.add(
        "description",
        text
    )

    cal.add_component(event)

    events_found += 1


with open(OUTPUT_FILE, "wb") as f:
    f.write(cal.to_ical())


print(f"Ace of Cups calendar updated: {events_found} events")
