import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event


OUTPUT_FILE = "aceofcups.ics"

BASE_URL = "https://aceofcupsbar.com/"
LOCATION = "Ace of Cups, 2619 N High St, Columbus, OH"

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text):
    match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})",
        text
    )

    if not match:
        return None

    month = MONTHS[match.group(1)]
    day = int(match.group(2))

    now = datetime.now()

    year = now.year
    date = datetime(year, month, day)

    if date < now - timedelta(days=30):
        date = datetime(year + 1, month, day)

    return date.replace(hour=19)


cal = Calendar()
cal.add("prodid", "-//Ace of Cups Calendar//")
cal.add("version", "2.0")
cal.add("X-WR-CALNAME", "Ace of Cups")


events = set()

for page in range(1, 10):

    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?list1page={page}"

    r = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text("\n")

    lines = [
        clean(x)
        for x in text.splitlines()
        if clean(x)
    ]

    for i, line in enumerate(lines):

        if not re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}",
            line
        ):
            continue

        event_date = parse_date(line)

        if not event_date:
            continue

        if i + 1 >= len(lines):
            continue

        title = lines[i + 1]

        if (
            title in events
            or "Ace of Cups" in title
            or title.startswith("at Ace")
        ):
            continue

        events.add(title)

        description_parts = []

        for extra in lines[i+2:i+8]:
            if (
                "$" in extra
                or "All Ages" in extra
                or "21+" in extra
                or "18+" in extra
            ):
                description_parts.append(extra)

        event = Event()

        event.add(
            "uid",
            f"aceofcups-{len(events)}@calendar"
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
            event_date
        )

        event.add(
            "dtend",
            event_date + timedelta(hours=3)
        )

        event.add(
            "location",
            LOCATION
        )

        event.add(
            "description",
            " | ".join(description_parts)
        )

        cal.add_component(event)


with open(OUTPUT_FILE, "wb") as f:
    f.write(cal.to_ical())


print(f"Ace of Cups calendar updated with {len(events)} events.")
