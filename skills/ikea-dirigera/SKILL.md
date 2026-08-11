---
name: ikea-dirigera
description: "Control IKEA smart lights and scenes via a DIRIGERA hub using ikea_cli.py."
version: 1.0.0
author: joost
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3]
required_environment_variables:
  - name: DIRIGERA_HOST
    prompt: IP address of your DIRIGERA hub on the local LAN (e.g. 192.168.1.x)
    help: "Check your router's device list or the IKEA Home smart app if unsure."
  - name: DIRIGERA_TOKEN
    prompt: DIRIGERA access token
    help: "Not something you type from memory - run `scripts/pair.py <hub-ip>` first (press the hub's physical Action button when prompted), then paste the token it prints."
metadata:
  hermes:
    tags: [Smart-Home, IKEA, DIRIGERA, Lights, IoT, Automation]
    homepage: https://github.com/Leggin/dirigera
---

# IKEA DIRIGERA CLI

Control IKEA smart lights (TRÅDFRI bulbs) and scenes via a DIRIGERA hub, using
a small local Python CLI (`scripts/ikea_cli.py`) — not a public cloud API,
this talks directly to the hub's local REST API over your LAN.

## Prerequisites

Install this skill's own venv, then pair with your hub:

```bash
cd <skill-install-dir>
uv venv .venv && uv pip install --python .venv/bin/python -e .
cp .env.example .env
.venv/bin/python scripts/pair.py <hub-ip>   # press the hub's Action button when prompted
# copy the printed DIRIGERA_HOST / DIRIGERA_TOKEN into .env
```

The hub's IP is usually something like `192.168.1.x` on your home LAN - check
your router's device list or the IKEA Home smart app if unsure. If commands
start timing out after setup, check that whatever runs this script can
actually reach the hub's LAN (same network, VPN route, etc.) - that's the
first thing to check before suspecting the script itself.

## When to Use

- "Turn on/off the [lights / a specific light]"
- "Dim the [room] lights" or set brightness
- "Trigger a scene" (scenes are configured in the IKEA Home smart app, not here)
- Checking which lights/devices are online

## Common Commands

Always run via the venv's own interpreter, from the tool's directory:

```bash
cd <skill-install-dir>
.venv/bin/python scripts/ikea_cli.py <command> [args]
```

### List

```bash
.venv/bin/python scripts/ikea_cli.py list          # every device (lights, sensors, remotes)
.venv/bin/python scripts/ikea_cli.py list-lights   # lights only, with on/off + brightness
```

### Control a light (by name, case-insensitive)

```bash
.venv/bin/python scripts/ikea_cli.py on "Kitchen Light"
.venv/bin/python scripts/ikea_cli.py off "Kitchen Light"
.venv/bin/python scripts/ikea_cli.py brightness "Kitchen Light" 50   # 1-100
```

### Scenes

```bash
.venv/bin/python scripts/ikea_cli.py scene "Living Room: Go to bed"
```

Scene names must match exactly what's configured in the DIRIGERA app — run
`list` first if unsure, shortcut-controller device names often hint at scene
names too (e.g. "Bedroom: Go to sleep").

## Notes

- Light names are case-insensitive but must otherwise match exactly — run
  `list-lights` to check exact names before controlling one.
- Some devices show up in `list` that aren't lights (remotes, motion sensors,
  door/window sensors) — `list-lights` filters to just the controllable lights.
- The hub is unofficial-API based (no IKEA cloud dependency) — hub firmware
  updates could occasionally change behavior; if something that used to work
  stops working, that's worth checking before assuming the script broke.
- `.env`'s `DIRIGERA_TOKEN` is a real long-lived credential for the physical
  hub — treat it like any other secret, don't print/log it.
