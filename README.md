# Astronomical ([site](https://divinetomedy.github.io/astronomical/))

A subscribable calendar feed of **solstices, equinoxes, and full & new moons** —
computed astronomically and accurate for the next ~1000 years.

Events appear as **all-day banners** with the event time built into the title,
e.g. `🌕 Full Moon (2:03am PDT)`. Feeds are available in **Pacific Time** and **UTC**
— pick the one that matches how you want the times to read.

## Subscribe in Google Calendar

1. Open [Google Calendar](https://calendar.google.com) on the web.
2. In the left sidebar, next to **Other calendars**, click **+** → **From URL**.
3. Paste one of the feed URLs below and click **Add calendar**.
4. To get emails, open that calendar's settings and add an **All-Day Event Notification**.

> Subscribing by URL keeps the calendar in sync automatically. Google refreshes
> on its own schedule (often every 12–24h), but since these dates never change,
> you only ever need to add it once.

### Feed URLs

The easiest way to grab a URL is the [landing page](https://divinetomedy.github.io/astronomical/),
which has a Pacific/UTC toggle and copy buttons. Direct links:

**Pacific Time**

| Range | Events | Size | URL |
|------|--------|------|-----|
| **100 years** (recommended) | ~2,900 | ~0.7 MB | `https://divinetomedy.github.io/astronomical/astronomical-pacific-100yr.ics` |
| 1000 years (full) | ~28,800 | ~6.7 MB | `https://divinetomedy.github.io/astronomical/astronomical-pacific.ics` |

**UTC**

| Range | Events | Size | URL |
|------|--------|------|-----|
| **100 years** (recommended) | ~2,900 | ~0.7 MB | `https://divinetomedy.github.io/astronomical/astronomical-utc-100yr.ics` |
| 1000 years (full) | ~28,800 | ~6.7 MB | `https://divinetomedy.github.io/astronomical/astronomical-utc.ics` |

**Which one?** Start with a 100-year feed — it covers your lifetime many times
over and loads reliably. Google Calendar can be unreliable with very large feeds,
so only use a 1000-year file if you specifically want the longer horizon.

> Other apps (Apple Calendar, Outlook, etc.) support the same URLs. In Apple
> Calendar: **File → New Calendar Subscription**.

## What's included

- 🌱 Vernal Equinox · ☀️ June Solstice · 🍁 Autumnal Equinox · 🌌 December Solstice
- 🌕 Full Moon · 🌑 New Moon

Each title includes the event's time and timezone, e.g. `☀️ June Solstice (1:25am PDT)`.
The season's hemisphere note is in the event description.

## Notes on times

- Times in titles are wall-clock times in the feed's timezone. Pacific feeds
  account for daylight saving (PST/PDT); far-future dates assume today's DST rules.
- The all-day banner falls on the event's date **in that timezone**, so an event
  just before/after midnight can land on different days in the Pacific vs. UTC feeds.

## Regenerating / changing the feeds

Feeds are produced by `generate.py` using the
[Astronomy Engine](https://github.com/cosinekitty/astronomy) library.

```bash
pip3 install --user astronomy-engine tzdata

python3 generate.py                          # regenerate all standard feeds
python3 generate.py pacific 2026 2126 out.ics  # one custom feed (utc | pacific)
```

To add another timezone, add an entry to `TIMEZONES` and a row to `FEEDS` in
`generate.py`, then update the toggle in `index.html`.

## Adding more event types later

`generate.py` is structured so new event types (e.g. eclipses, meteor showers,
planetary conjunctions, perihelion/aphelion) can be added as additional
collectors. Astronomy Engine supports eclipses and apsides directly.
