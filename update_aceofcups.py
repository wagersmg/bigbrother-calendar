import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event


OUTPUT_FILE = "aceofcups.ics"

BASE_URL = "https://aceofcupsbar.com/"
LOCATION = "Ace of Cups, 2619 N High St, Columbus, OH"


MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def parse_date(text):
    match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)",
        text,
    )

    if not match:
        return None

    month = MONTHS[match.group(1)]
    day = int(match.group(2))

    now = datetime.now()

    year = now.year

    event_date = datetime(
        year,
        month,
        day,
        19,
        0,
    )

    # Handle events that have already passed this year
    if event_date < now - timedelta(days=30):
        event_date = event_date.replace(year=year + 1)

    return event_date


cal = Calendar()
cal.add("prodid", "-//Ace of Cups Calendar//")
cal.add("version", "2.0")
cal.add("X-WR-CALNAME", "Ace of Cups")


events_added = 0
seen = set()


for page in range(1, 10):

    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?list1page={page}"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")


    cards = soup.select(
        ".seetickets-list-event-container"
    )

    if not cards:
        break


    for card in cards:

        title_element = card.select_one(
            ".event-title a"
        )

        date_element = card.select_one(
            ".event-date"
        )

        if not title_element or not date_element:
            continue


        title = title_element.get_text(
            " ",
            strip=True
        )

        if title in seen:
            continue

        seen.add(title)


        start = parse_date(
            date_element.get_text(
                " ",
                strip=True
            )
        )

        if not start:
            continue


        ticket_url = title_element.get(
            "href"
        )


        headliners = card.select_one(
            ".headliners"
        )

        ages = card.select_one(
            ".ages"
        )

        price = card.select_one(
            ".price"
        )

        genre = card.select_one(
            ".genre"
        )


        description = []

        if headliners:
            description.append(
                "Artists: " +
                headliners.get_text(strip=True)
            )

        if genre:
            description.append(
                "Genre: " +
                genre.get_text(strip=True)
            )

        if ages:
            description.append(
                "Age: " +
                ages.get_text(strip=True)
            )

        if price:
            description.append(
                "Price: " +
                price.get_text(strip=True)
            )

        if ticket_url:
            description.append(
                "Tickets: " +
                ticket_url
            )


        event = Event()

        event.add(
            "uid",
            f"aceofcups-{events_added}@calendar"
        )

        event.add(
            "dtstamp",
            datetime.now(timezone.utc)
        )

        event.add(
            "summary",
            "Ace of Cups - " + title
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
            "\n".join(description)
        )

        cal.add_component(event)

        events_added += 1


with open(OUTPUT_FILE, "wb") as f:
    f.write(cal.to_ical())


print(
    f"Ace of Cups calendar updated with {events_added} events."
)
