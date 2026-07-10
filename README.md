# mgw-calendar

Auto-updating Google Calendar feeds. 

[Big Brother (US)](https://www.tvmaze.com/shows/1453/big-brother) and [Big Brother Unlocked](https://www.tvmaze.com/shows/84768/big-brother-unlocked), built from TVMaze episode data.

[Ace of Cups](https://aceofcupsbar.com/) events, built from venue website.

A GitHub Action runs daily, regenerates `*.ics`, and commits it if
anything changed. Subscribe to the raw file URL in Google Calendar and it'll
stay in sync automatically (Google re-checks subscribed calendars roughly
every 12–24 hours).

## Subscribe in Google Calendar

1. Go to Google Calendar → Settings → **Add calendar** → **From URL**
2. Paste URL (https://raw.githubusercontent.com/wagers/mgw-calendar/main/calendar_name.ics)
3. Click **Add calendar**
