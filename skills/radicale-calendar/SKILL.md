---
name: radicale-calendar
description: "Check, create, reschedule, and delete calendar appointments via Radicale (self-hosted CalDAV) using the caldav Python library."
version: 1.0.0
author: joost
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Calendar, CalDAV, Radicale, Scheduling]
    homepage: https://radicale.org
---

# Radicale Calendar

Check, create, reschedule, and delete appointments on a self-hosted
[Radicale](https://radicale.org) CalDAV calendar via a small CLI wrapper
(`scripts/radicale_cli.py`) around the `caldav` Python library. Talks
directly to your own Radicale server - not a public cloud calendar, no
OAuth flow, just a URL + basic auth.

## Prerequisites

Install this skill's own venv, then point it at your Radicale instance:

```bash
cd <skill-install-dir>
uv venv .venv && uv pip install --python .venv/bin/python -e .
cp .env.example .env   # then fill in RADICALE_URL / RADICALE_USERNAME / RADICALE_PASSWORD
```

Script and skill docs live together in this one directory (venv, `.env`,
`scripts/`) rather than split across separate tool/doc paths - keeps the
whole thing self-contained and easy to relocate.

## When to Use

- "What's on my calendar [today / this week / on X date]?"
- "Do I have anything on [date/time]?" (check for conflicts before agreeing to something)
- "Add an appointment for..." / "Schedule a meeting..."
- "Move my [X] appointment to..." / "Reschedule..."
- "Cancel my [X] appointment"

## Common Commands

Always run via the venv's own interpreter, from the tool's directory:

```bash
cd <skill-install-dir>
.venv/bin/python scripts/radicale_cli.py <command> [args]
```

All commands return JSON on stdout. Parse it, don't eyeball raw text.

### List calendars

```bash
.venv/bin/python scripts/radicale_cli.py list-calendars
```

### List events (defaults to the next 7 days if no --start/--end given)

```bash
.venv/bin/python scripts/radicale_cli.py list-events
.venv/bin/python scripts/radicale_cli.py list-events --start 2026-08-12T00:00:00 --end 2026-08-19T00:00:00
```

Returns `[{uid, summary, start, end, location, description, calendar}]`.

### Create an event

```bash
.venv/bin/python scripts/radicale_cli.py create-event \
  --summary "Dentist" --start 2026-08-15T14:00:00 --end 2026-08-15T15:00:00 \
  --location "Downtown Clinic" --description "Check-up"
```

Returns `{status: "created", uid, summary, start, end, ...}` - the `uid` is
needed for rescheduling/deleting later.

### Create an all-day / recurring event (e.g. a birthday or anniversary)

```bash
.venv/bin/python scripts/radicale_cli.py create-event \
  --summary "🎂 Someone's Birthday" --start 1990-04-13 --all-day --recur yearly
```

`--all-day` takes a bare `YYYY-MM-DD` (no time) and produces a proper
whole-day event (`DTSTART;VALUE=DATE`, not a timed one) - `--end` defaults to
the day after `--start` if omitted (iCal's DTEND is exclusive, so a
single-day all-day event's end is technically the next day). `--recur
yearly` adds `RRULE:FREQ=YEARLY` - `list-events` correctly expands it into
future years without needing to re-create the event annually.

Tip: for recurring personal dates (birthdays, anniversaries) where the real
year matters for age math elsewhere, set `--start`'s year to the real one
and use `--description` as a marker your own automation can check (e.g.
`"birth year known"` vs `"birth year unknown"` if you use a placeholder
year) - events here are name-only, no age is shown or computed by this
skill itself.

### Reschedule an event (change when it happens)

```bash
.venv/bin/python scripts/radicale_cli.py reschedule-event \
  --uid <uid-from-list-or-create> --start 2026-08-16T14:00:00 --end 2026-08-16T15:00:00
```

**Note the naming**: this is `reschedule-event`, not `move-event` -
deliberately, to avoid ambiguity with other CalDAV tools where "move" means
transferring an event to a *different calendar*. This changes the
date/time only.

### Update other fields (summary/location/description, not the time)

```bash
.venv/bin/python scripts/radicale_cli.py update-event --uid <uid> --location "New location"
```

Pass an empty string (`--location ""`) to clear a field entirely rather
than leaving it set.

### Delete an event

```bash
.venv/bin/python scripts/radicale_cli.py delete-event --uid <uid>
```

## Rules

1. **Never create, reschedule, or delete an event without confirming with
   the user first.** Show what will be created/changed/removed (summary,
   date/time, location) and get explicit confirmation before running the
   command. Listing/checking events needs no confirmation.
2. **Always include a timezone-aware or explicit local ISO 8601 timestamp**
   for `--start`/`--end`. If a time is given without a date, resolve the
   actual date before calling anything (check today's date, don't guess).
3. **Get the `uid` from `list-events` or `create-event`'s own output**
   before rescheduling/updating/deleting - don't guess or invent one.
4. **If only one calendar exists**, commands default to it and no
   `--calendar` flag is needed. Once more than one calendar exists, check
   `list-calendars` first rather than assuming which one is meant.
