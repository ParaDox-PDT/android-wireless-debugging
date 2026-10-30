#!/usr/bin/env python3
"""Pair and connect Android phones or tablets over Wi-Fi using ADB."""

from __future__ import annotations

import ipaddress
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


class AdbError(RuntimeError):
    """Raised when an ADB command or connection verification fails."""


def find_adb() -> str:
    """Find ADB on PATH or in common Android SDK directories."""
    executable = "adb.exe" if os.name == "nt" else "adb"
    found = shutil.which("adb")
    if found:
        return found

    locations = [os.environ.get("ANDROID_HOME"), os.environ.get("ANDROID_SDK_ROOT")]
    if os.environ.get("LOCALAPPDATA"):
        locations.append(str(Path(os.environ["LOCALAPPDATA"]) / "Android" / "Sdk"))
    locations.extend([
        str(Path.home() / "Android" / "Sdk"),
        str(Path.home() / "Library" / "Android" / "sdk"),
    ])

    for location in filter(None, locations):
        candidate = Path(location) / "platform-tools" / executable
        if candidate.is_file():
            return str(candidate)

    raise AdbError("ADB not found. Install Android SDK Platform-Tools or add adb to PATH.")


def parse_address(raw: str) -> str:
    """Validate IPv4 and TCP port, returning normalized IP:PORT."""
    try:
        host, port = raw.strip().rsplit(":", 1)
        ip = ipaddress.IPv4Address(host)
        if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return f"{ip}:{int(port)}"
    except (ValueError, TypeError) as exc:
        raise ValueError(
            "Enter a valid IPv4 address and port, e.g. 192.168.1.42:37123"
        ) from exc


def read_address(prompt: str) -> str:
    while True:
        try:
            return parse_address(input(prompt))
        except ValueError as exc:
            print(f"Invalid address: {exc}")


def read_pairing_code() -> str:
    while True:
        code = input("Step 2/3 - Enter the 6-digit pairing code: ").strip()
        if re.fullmatch(r"[0-9]{6}", code):
            return code
        print("Invalid code. Enter exactly six digits.")


def run_adb(adb: str, *args: str) -> str:
    """Run an ADB command with a 30-second timeout."""
    result = subprocess.run(
        [adb, *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30, check=False,
    )
    output = "\n".join(
        part.strip() for part in (result.stdout, result.stderr) if part.strip()
    )
    if output:
        print(output)
    if result.returncode != 0:
        raise AdbError(
            f"ADB command failed (exit {result.returncode}). "
            "Check IP, port, and device permissions."
        )
    return output


def main() -> int:
    print("=== Android Wireless Debugging Connector ===")
    adb = find_adb()
    print(f"Using ADB: {adb}")
    print("Connect your computer and Android device to the same local network.")
    print("On Android: Settings > Developer options > Wireless debugging.\n")

    print("Open 'Pair device with pairing code' on your Android device.")
    pairing_address = read_address(
        "Step 1/3 - Enter PAIRING IP address and port: "
    )
    pairing_code = read_pairing_code()
    pairing_result = run_adb(adb, "pair", pairing_address, pairing_code)
    if "successfully paired" not in pairing_result.lower():
        raise AdbError("Pairing was not confirmed. Open a new pairing code and retry.")

    print("\nPairing successful. Close the pairing code dialog.")
    print("Go back to the MAIN Wireless debugging screen.")
    print("The connection port usually differs from the pairing port.")
    connection_address = read_address(
        "Step 3/3 - Enter DEVICE IP address and port: "
    )
    connect_result = run_adb(adb, "connect", connection_address)
    if (
        "connected to" not in connect_result.lower()
        and "already connected to" not in connect_result.lower()
    ):
        raise AdbError("ADB did not confirm a connection. Check the connection address.")

    state = run_adb(adb, "-s", connection_address, "get-state")
    if state.strip() != "device":
        raise AdbError(
            "Device is not ready. Check Wireless debugging and device authorization."
        )

    print("\nConnected devices:")
    run_adb(adb, "devices", "-l")
    print("\nSuccess! Select your Android device in Android Studio.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(130)
    except EOFError:
        print("\nInput was closed. Run the script in an interactive terminal.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("\nADB timed out after 30 seconds. Check your network and ports.")
        sys.exit(1)
    except (AdbError, OSError) as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
