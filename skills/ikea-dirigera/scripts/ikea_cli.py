"""Command-line wrapper around ikea_dirigera, shaped to match the openhue CLI
(see the Hermes smart-home/openhue skill) so an agent can shell out to it the
same way: `ikea list`, `ikea on "Living Room"`, `ikea brightness "Living Room" 50`.

Reads DIRIGERA_HOST / DIRIGERA_TOKEN from a .env file in the skill's root
directory by default (override with --env-path).

Run: python scripts/ikea_cli.py <command> [args]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ikea_dirigera import DirigeraClient
from ikea_dirigera.client import DeviceStatus

DEFAULT_ENV_PATH = str(Path(__file__).resolve().parent.parent / ".env")


def _find_light(client: DirigeraClient, name: str) -> DeviceStatus:
    """Case-insensitive name match, matching openhue's light-by-name UX."""
    lights = client.list_lights()
    matches = [light for light in lights if light.name.lower() == name.lower()]
    if not matches:
        available = ", ".join(sorted(light.name for light in lights))
        print(f"No light named '{name}'. Available: {available}", file=sys.stderr)
        sys.exit(1)
    return matches[0]


def cmd_list(client: DirigeraClient, args: argparse.Namespace) -> None:
    devices = client.list_devices()
    for d in sorted(devices, key=lambda d: not d.is_reachable):
        flag = "OFFLINE" if not d.is_reachable else "online "
        light = f"  on={d.is_on} brightness={d.brightness}" if d.is_on is not None else ""
        print(f"[{flag}] {d.name:<25} {d.device_type:<12} {d.model:<20}{light}")


def cmd_list_lights(client: DirigeraClient, args: argparse.Namespace) -> None:
    for light in client.list_lights():
        state = "on " if light.is_on else "off"
        print(f"{light.name:<25} {state}  brightness={light.brightness}")


def cmd_on(client: DirigeraClient, args: argparse.Namespace) -> None:
    light = _find_light(client, args.name)
    client.set_light_state(light.id, True)
    print(f"{light.name}: on")


def cmd_off(client: DirigeraClient, args: argparse.Namespace) -> None:
    light = _find_light(client, args.name)
    client.set_light_state(light.id, False)
    print(f"{light.name}: off")


def cmd_brightness(client: DirigeraClient, args: argparse.Namespace) -> None:
    if not 1 <= args.level <= 100:
        print("brightness level must be 1-100", file=sys.stderr)
        sys.exit(1)
    light = _find_light(client, args.name)
    client.set_light_brightness(light.id, args.level)
    print(f"{light.name}: brightness={args.level}")


def cmd_scene(client: DirigeraClient, args: argparse.Namespace) -> None:
    client.trigger_scene(args.name)
    print(f"triggered scene: {args.name}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="ikea", description="Control an IKEA DIRIGERA hub.")
    parser.add_argument(
        "--env-path", default=DEFAULT_ENV_PATH, help="Path to .env with DIRIGERA_HOST/TOKEN"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List every device on the hub").set_defaults(func=cmd_list)
    sub.add_parser("list-lights", help="List lights only").set_defaults(func=cmd_list_lights)

    p_on = sub.add_parser("on", help="Turn a light on")
    p_on.add_argument("name")
    p_on.set_defaults(func=cmd_on)

    p_off = sub.add_parser("off", help="Turn a light off")
    p_off.add_argument("name")
    p_off.set_defaults(func=cmd_off)

    p_bright = sub.add_parser("brightness", help="Set a light's brightness (1-100)")
    p_bright.add_argument("name")
    p_bright.add_argument("level", type=int)
    p_bright.set_defaults(func=cmd_brightness)

    p_scene = sub.add_parser("scene", help="Trigger a scene by name")
    p_scene.add_argument("name")
    p_scene.set_defaults(func=cmd_scene)

    args = parser.parse_args()
    client = DirigeraClient.from_env(args.env_path)
    args.func(client, args)


if __name__ == "__main__":
    main()
