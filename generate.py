#!/usr/bin/env python3
"""
Generate iCalendar (.ics) feeds of astronomical events.

Currently produces:
  - Solstices & equinoxes (4 per year)
  - Full & new moons

Each event is an all-day banner whose title includes the local clock time of the
event, e.g. "Full Moon (3:14am)". The banner's date and the displayed time are
both rendered in the feed's timezone. Astronomical instants are computed in UTC
with the Astronomy Engine library, then converted.

A "feed" is one (timezone, year-range) combination. With no arguments this
script regenerates the full standard set of feeds (see FEEDS below).

Usage:
    python3 generate.py                         # regenerate all standard feeds
    python3 generate.py pacific 2026 2126 out.ics   # one custom feed
        (timezone is "utc" or "pacific")
"""

import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import astronomy

PRODID = "-//astronomical//Astronomical Events//EN"

# Supported timezones: key -> (label, IANA name).
TIMEZONES = {
    "utc": ("UTC", "UTC"),
    "pacific": ("Pacific", "America/Los_Angeles"),
}

# Standard feeds to (re)generate when run with no arguments:
# (timezone_key, start_year, end_year, output_path)
THIS_YEAR = datetime.now(timezone.utc).year
FEEDS = [
    ("pacific", THIS_YEAR, THIS_YEAR + 100, "astronomical-pacific-100yr.ics"),
    ("pacific", THIS_YEAR, THIS_YEAR + 1000, "astronomical-pacific.ics"),
    ("utc", THIS_YEAR, THIS_YEAR + 100, "astronomical-utc-100yr.ics"),
    ("utc", THIS_YEAR, THIS_YEAR + 1000, "astronomical-utc.ics"),
]

# Moon quarter index -> (emoji, label). 0=new, 1=first quarter, 2=full, 3=last.
MOON_PHASES = {
    0: ("\U0001F311", "New Moon"),
    2: ("\U0001F315", "Full Moon"),
}

# Season attribute -> (emoji, title, hemisphere note).
SEASONS = [
    ("mar_equinox", "\U0001F331", "Vernal Equinox", "Spring in the N. Hemisphere, autumn in the S."),
    ("jun_solstice", "\U00002600\U0000FE0F", "June Solstice", "Summer in the N. Hemisphere, winter in the S."),
    ("sep_equinox", "\U0001F341", "Autumnal Equinox", "Autumn in the N. Hemisphere, spring in the S."),
    ("dec_solstice", "\U0001F30C", "December Solstice", "Winter in the N. Hemisphere, summer in the S."),
]


def ics_escape(text):
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    """Fold long lines to 75 octets per RFC 5545."""
    if len(line.encode("utf-8")) <= 75:
        return line
    out = []
    chunk = b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(chunk) + len(b) > 75:
            out.append(chunk.decode("utf-8"))
            chunk = b" " + b  # continuation lines start with a space
        else:
            chunk += b
    out.append(chunk.decode("utf-8"))
    return "\r\n".join(out)


def clock(dt_local):
    """Compact clock time with timezone abbreviation, e.g. '3:14am PST', '10:03am UTC'."""
    return dt_local.strftime("%-I:%M") + dt_local.strftime("%p").lower() + " " + dt_local.strftime("%Z")


def make_event(dt_local, emoji, label, note, uid_kind, dtstamp):
    """Build an all-day VEVENT from a timezone-aware local datetime."""
    date = dt_local.date()
    start = date.strftime("%Y%m%d")
    end = (date + timedelta(days=1)).strftime("%Y%m%d")
    uid = f"{uid_kind}-{dt_local.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%S')}@astronomical"
    summary = f"{emoji} {label} ({clock(dt_local)})"

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{start}",
        f"DTEND;VALUE=DATE:{end}",
        f"SUMMARY:{ics_escape(summary)}",
        "TRANSP:TRANSPARENT",
        f"CATEGORIES:{ics_escape('Astronomical')}",
    ]
    if note:
        lines.append(f"DESCRIPTION:{ics_escape(note)}")
    lines.append("END:VEVENT")
    return [fold(l) for l in lines]


def collect_events(start_year, end_year, tz):
    """Return events as (local_datetime, emoji, label, note, uid_kind), sorted."""
    events = []

    # Seasons: one call per year.
    for year in range(start_year, end_year + 1):
        s = astronomy.Seasons(year)
        for attr, emoji, label, note in SEASONS:
            dt = getattr(s, attr).Utc().replace(tzinfo=timezone.utc).astimezone(tz)
            events.append((dt, emoji, label, note, "season"))

    # Moon phases: walk quarters across the range.
    start_time = astronomy.Time.Make(start_year, 1, 1, 0, 0, 0)
    end_utc = datetime(end_year + 1, 1, 1, tzinfo=timezone.utc)
    mq = astronomy.SearchMoonQuarter(start_time)
    while True:
        dt = mq.time.Utc().replace(tzinfo=timezone.utc)
        if dt >= end_utc:
            break
        if mq.quarter in MOON_PHASES:
            emoji, label = MOON_PHASES[mq.quarter]
            events.append((dt.astimezone(tz), emoji, label, "", "moon"))
        mq = astronomy.NextMoonQuarter(mq)

    events.sort(key=lambda e: e[0])
    return events


def build_calendar(start_year, end_year, tz_key):
    label, iana = TIMEZONES[tz_key]
    tz = ZoneInfo(iana)
    cal_name = f"Astronomical ({label}): Full/New Moons + Solstices/Equinoxes"
    cal_desc = f"Solstices, equinoxes, and full & new moons. Times shown in {label}."
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    out = [fold(l) for l in [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{ics_escape(cal_name)}",
        f"X-WR-CALDESC:{ics_escape(cal_desc)}",
        "REFRESH-INTERVAL;VALUE=DURATION:P30D",
        "X-PUBLISHED-TTL:P30D",
    ]]

    events = collect_events(start_year, end_year, tz)
    for dt, emoji, label_, note, kind in events:
        out.extend(make_event(dt, emoji, label_, note, kind, dtstamp))

    out.append("END:VCALENDAR")
    return "\r\n".join(out) + "\r\n", len(events)


def write_feed(tz_key, start_year, end_year, out_path):
    text, count = build_calendar(start_year, end_year, tz_key)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    label = TIMEZONES[tz_key][0]
    print(f"Wrote {count:>6} events  {label:<8} {start_year}-{end_year}  "
          f"-> {out_path}  [{len(text.encode('utf-8')) / 1_000_000:.1f} MB]")


def main():
    args = sys.argv[1:]
    if not args:
        for feed in FEEDS:
            write_feed(*feed)
        return

    tz_key = args[0].lower()
    if tz_key not in TIMEZONES:
        sys.exit(f"Unknown timezone '{tz_key}'. Choose one of: {', '.join(TIMEZONES)}")
    start_year = int(args[1]) if len(args) > 1 else THIS_YEAR
    end_year = int(args[2]) if len(args) > 2 else THIS_YEAR + 1000
    out_path = args[3] if len(args) > 3 else f"astronomical-{tz_key}.ics"
    write_feed(tz_key, start_year, end_year, out_path)


if __name__ == "__main__":
    main()
