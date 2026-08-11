"""Interactive first-time pairing with the DIRIGERA hub.

Run once: python scripts/pair.py <hub-ip>
Prompts you to press the physical Action button on the underside of the hub,
then prints a long-lived access token to save into .env as DIRIGERA_TOKEN.
"""

from __future__ import annotations

import sys

from ikea_dirigera import DirigeraClient


def main(host: str) -> None:
    token = DirigeraClient.pair(host)

    print("\nPairing succeeded. Add these to your .env:\n")
    print(f"DIRIGERA_HOST={host}")
    print(f"DIRIGERA_TOKEN={token}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: py -3 pair.py <hub-ip>")
        sys.exit(1)
    main(sys.argv[1])
