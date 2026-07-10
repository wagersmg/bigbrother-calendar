# bigbrother-calendar

Auto-updating Google Calendar feed for CBS's Big Brother (US), built from
[TVMaze](https://www.tvmaze.com/shows/1453/big-brother) episode data.

A GitHub Action runs daily, regenerates `bigbrother.ics`, and commits it if
anything changed. Subscribe to the raw file URL in Google Calendar and it'll
stay in sync automatically (Google re-checks subscribed calendars roughly
every 12–24 hours).

## Subscribe in Google Calendar

1. Go to Google Calendar → Settings → **Add calendar** → **From URL**
2. Paste:
   `https://raw.githubusercontent.com/<your-username>/bigbrother-calendar/main/bigbrother.ics`
3. Click **Add calendar**

## Local run

```
pip install -r requirements.txt
python update_calendar.py
```
