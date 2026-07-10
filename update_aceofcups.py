import re
import hashlib
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


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


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

    event_date = datetime(
        now.year,
        month,
        day,
        19,
        0,
    )

    if event_date < now - timedelta(days=30):
        event_date = event_date.replace(
            year=now.year + 1
        )

    return event_date


def get_event_times(url):
    """
    Gets start/end times from the ticket page.
    Example:
    10:00 PM - 1:00 AM EDT
    """

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        text = soup.get_text(
            " ",
            strip=True,
        )

        match = re.search(
            r"(\d{1,2}:\d{2}\s?(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s?(?:AM|PM))",
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return None, None

        return (
            match.group(1),
            match.group(2),
        )

    except Exception as e:
        print(
            f"Could not get times for {url}: {e}"
        )

        return None, None


def apply_time(base_date, time_text):
    if not time_text:
        return base_date

    parsed = datetime.strptime(
        time_text.upper().replace(" ", ""),
        "%I:%M%p",
    )

    return base_date.replace(
        hour=parsed.hour,
        minute=parsed.minute,
    )


cal = Calendar()

cal.add(
    "prodid",
    "-//Ace of Cups Calendar//"
)

cal.add(
    "version",
    "2.0"
)

cal.add(
    "X-WR-CALNAME",
    "Ace of Cups"
)


events_added = 0
seen = set()


for page in range(1, 10):

    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?list1page={page}"


    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    )

    response.raise_for_status()


    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )


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


        ticket_url = title_element.get(
            "href",
            "",
        )


        if ticket_url in seen:
            continue

        seen.add(ticket_url)


        headliner_element = card.select_one(
            ".headliners"
        )

        headliner = ""

        if headliner_element:
            headliner = clean(
                headliner_element.get_text()
            )


        if headliner:
            title = headliner
        else:
            title = clean(
                title_element.get_text()
            )


        title = re.sub(
            r"\s+at Ace of Cups$",
            "",
            title,
            flags=re.IGNORECASE,
        )


        start = parse_date(
            date_element.get_text()
        )


        if not start:
            continue


        start_time, end_time = get_event_times(
            ticket_url
        )


        start = apply_time(
            start,
            start_time,
        )


        if end_time:
            end = apply_time(
                start,
                end_time,
            )

            # Handle events ending after midnight
            if end <= start:
                end += timedelta(days=1)

        else:
            end = start + timedelta(hours=3)


        description = []


        genre = card.select_one(
            ".genre"
        )

        ages = card.select_one(
            ".ages"
        )

        price = card.select_one(
            ".price"
        )


        if genre:
            description.append(
                f"Genre: {clean(genre.get_text())}"
            )

        if ages:
            description.append(
                f"Age: {clean(ages.get_text())}"
            )

        if price:
            description.append(
                f"Price: {clean(price.get_text())}"
            )

        if ticket_url:
            description.append(
                f"Tickets: {ticket_url}"
            )


        uid = hashlib.md5(
            ticket_url.encode()
        ).hexdigest()


        event = Event()


        event.add(
            "uid",
            f"aceofcups-{uid}@calendar",
        )

        event.add(
            "dtstamp",
            datetime.now(timezone.utc),
        )

        event.add(
            "summary",
            title,
        )

        event.add(
            "dtstart",
            start,
        )

        event.add(
            "dtend",
            end,
        )

        event.add(
            "location",
            LOCATION,
        )

        event.add(
            "description",
            "\n".join(description),
        )


        cal.add_component(event)

        events_added += 1


with open(
    OUTPUT_FILE,
    "wb",
) as f:
    f.write(
        cal.to_ical()
    )


print(
    f"Ace of Cups calendar updated with {events_added} events."
)
