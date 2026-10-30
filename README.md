# Android Wireless Debugging Connector 🐍📱

A lightweight, cross-platform Python CLI for pairing and connecting **Android phones and tablets** to Android Studio over Wi-Fi using ADB.

It guides you through exactly three steps: **pairing IP:port → 6-digit pairing code → device IP:port**.

No third-party Python packages required.

## Features

- Finds `adb` on `PATH` or in common Android SDK locations on Windows, macOS, and Linux.
- Validates the IPv4 address and port for both pairing and connection.
- Runs `adb pair` with the six-digit code.
- Runs `adb connect` using the **separate** connection port.
- Verifies `adb get-state` returns `device`, then lists connected devices.
- Displays understandable errors and enforces a 30-second ADB timeout.

## Requirements

- Android 11 (API 30) or newer, with **Wireless debugging** enabled.
- Python 3.9+.
- Android SDK Platform-Tools (including `adb`); normally installed with Android Studio.
- A local network where the computer and Android device can communicate. Guest/corporate Wi-Fi may block peer connections.

Check your setup:

```bash
python --version
adb version
```

On Windows, use `py --version` if needed. If `adb` is not on `PATH`, the script searches common SDK directories.

## Quick start: three steps

Run:

```bash
python connect_android.py
```

**Step 1 — Pairing IP:Port**

On your Android device, go to **Settings → Developer options → Wireless debugging → Pair device with pairing code**. Keep the popup open and enter the **pairing IP address and port** shown in that popup.

**Step 2 — Six-digit code**

Enter the six-digit Wi-Fi pairing code shown in the same popup. The script runs `adb pair`.

**Step 3 — Device IP:Port**

After pairing succeeds, close the popup. On the **main Wireless debugging screen**, find **IP address & Port** and enter this address. The script runs `adb connect`, verifies device state, and prints your connected devices.

### Example terminal session

The addresses and pairing code below are examples, not real credentials.

```text
=== Android Wireless Debugging Connector ===
Using ADB: .../platform-tools/adb
Connect your computer and Android device to the same local network.
On Android: Settings > Developer options > Wireless debugging.

Open 'Pair device with pairing code' on your Android device.
Step 1/3 - Enter PAIRING IP address and port: 192.168.1.42:37123
Step 2/3 - Enter the 6-digit pairing code: 123456
Successfully paired to 192.168.1.42:37123 [...]

Pairing successful. Close the pairing code dialog.
Go back to the MAIN Wireless debugging screen.
The connection port usually differs from the pairing port.
Step 3/3 - Enter DEVICE IP address and port: 192.168.1.42:41587
connected to 192.168.1.42:41587
device

Connected devices:
List of devices attached
192.168.1.42:41587    device ...

Success! Select your Android device in Android Studio.
```

Your Android device should now appear in Android Studio's device selector.

## Pairing port vs connection port

**Do not use the pairing popup's port for `adb connect`.** The two screens usually show different ports.

| Action | Where to find details | ADB command |
| --- | --- | --- |
| Pair | `Pair device with pairing code` popup | `adb pair IP:PAIRING_PORT CODE` |
| Connect | Main `Wireless debugging` screen | `adb connect IP:DEVICE_PORT` |
| Verify | Terminal | `adb devices -l` |

Pairing typically persists until the device is unpaired. For a previously paired device, `adb connect IP:DEVICE_PORT` may be enough. **This CLI deliberately requests pairing on each run**, matching the requested three-step interaction.

## Troubleshooting

| Issue | What to do |
| --- | --- |
| `ADB not found` | Install Android SDK Platform-Tools, or add `platform-tools` to your `PATH`. |
| Pairing failed | Keep the pairing popup open. Check pairing IP, pairing port, and current six-digit code. |
| Connection failed/timed out | Confirm the devices can communicate on the network; use the **main-screen connection port**. |
| Device offline or unauthorized | Recheck the Wireless debugging authorization; disconnect and pair again. |
| Device absent from Android Studio | Try `adb devices -l`, verify SDK Platform-Tools and refresh the device selector. |
| IP or port changed | Read the current address on your device; it may change when reconnecting Wi-Fi. |

## Security

- Enable wireless debugging only on trusted networks, and disable it when not needed.
- The script passes the pairing code locally to your installed `adb` executable and does not persist it.
- Remove IP addresses, pairing codes, and device identifiers from publicly shared screenshots.

## Project structure

```text
android-wireless-debugging/
├── connect_android.py
├── README.md
├── tests/
│   └── test_connect_android.py
└── .gitignore
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

The unit tests validate input parsing and the three-step ADB flow using mocks, without a real device. End-to-end testing still requires Android hardware.

## Limitations

- IPv4 addresses only.
- Uses Android 11+ pairing-code-based wireless ADB, not legacy USB-based `adb tcpip 5555`.
- Does not auto-discover devices or scan your network.
- Requires an interactive terminal and the current details displayed on the device.

## Contributing

Contributions, issues, and pull requests are welcome. Please do not publish pairing codes or private device logs.
