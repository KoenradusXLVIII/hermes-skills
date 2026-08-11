"""Client wrapper around the `dirigera` library for one IKEA DIRIGERA hub."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

import dirigera
from dirigera.devices.device import StartupEnum
from dirigera.hub.auth import ALPHABET, CODE_LENGTH, get_token, random_code, send_challenge


@dataclass
class DeviceStatus:
    id: str
    name: str
    model: str
    device_type: str
    is_reachable: bool
    last_seen: datetime
    is_on: bool | None
    brightness: int | None  # light_level, 1-100


class DirigeraClient:
    """Wraps dirigera.Hub for one gateway."""

    def __init__(self, host: str, token: str) -> None:
        self._hub = dirigera.Hub(token=token, ip_address=host)

    @classmethod
    def from_env(cls, env_path: str = ".env") -> DirigeraClient:
        _load_dotenv(env_path)
        return cls(host=os.environ["DIRIGERA_HOST"], token=os.environ["DIRIGERA_TOKEN"])

    @staticmethod
    def pair(host: str, wait_for_button: bool = True) -> str:
        """Perform first-time pairing against the hub's physical Action button.

        Returns a long-lived access token to be stored for future connections.
        """
        code_verifier = random_code(ALPHABET, CODE_LENGTH)
        code = send_challenge(host, code_verifier)
        if wait_for_button:
            input("Press the Action button on the DIRIGERA hub, then hit ENTER...")
        return get_token(host, code, code_verifier)

    def list_devices(self) -> list[DeviceStatus]:
        return [_device_status(d) for d in self._hub.get_all_devices()]

    def list_lights(self) -> list[DeviceStatus]:
        return [_device_status(light) for light in self._hub.get_lights()]

    def set_light_state(self, light_id: str, on: bool) -> None:
        light = self._hub.get_light_by_id(light_id)
        light.set_light(on)

    def set_light_brightness(self, light_id: str, level: int) -> None:
        """level: 1-100."""
        light = self._hub.get_light_by_id(light_id)
        light.set_light_level(level)

    def set_light_startup_behaviour(self, light_id: str, behaviour: StartupEnum) -> None:
        """Controls what the light does when power is restored after an outage."""
        light = self._hub.get_light_by_id(light_id)
        light.set_startup_behaviour(behaviour)

    def trigger_scene(self, name: str) -> None:
        """Trigger a scene by the name configured for it in the DIRIGERA app."""
        scene = self._hub.get_scene_by_name(name)
        scene.trigger()


def _device_status(device) -> DeviceStatus:
    return DeviceStatus(
        id=device.id,
        name=device.attributes.custom_name,
        model=device.attributes.model,
        device_type=device.device_type,
        is_reachable=device.is_reachable,
        last_seen=device.last_seen,
        is_on=getattr(device.attributes, "is_on", None),
        brightness=getattr(device.attributes, "light_level", None),
    )


def _load_dotenv(env_path: str) -> None:
    """Load simple KEY=VALUE pairs from a .env file if present."""
    if not env_path or not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value
