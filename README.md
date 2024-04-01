# Sysmon: A Ready-to-Use System Monitor

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Preview
For a preview, see the [PREVIEW.md file](screens/PREVIEW.md).

## What is Sysmon?
Sysmon is a system monitor that is ready to use and easy to understand. It utilizes Linux's /proc pseudo filesystem to read information and curses to display it. All you need to do is clone this repository and run the sysmon file.

## What Can Sysmon Do?
- Display CPU information including model, temperature (1), frequency (2), cores (1), threads count, and cache memory size (1).
- Show memory information such as total, available, used (3), cached RAM, and swap information.
- Provide system load, entities, and uptime.
- Present the processes (6 by default) consuming the most VmRSS, including their state and name.
- Present network information such as device, transferred and received data, and speed.

1. Information reported might not be correct.

2. Frequency information may depend on the kernel and might not match the maximum frequency reported on the manufacturer's website.

3. There are two "used" columns because the calculations differ. "Actual used" represents a report similar to htop, while "used" equals MemTotal - MemAvailable.

## Using Sysmon
Clone the repository:
```sh
git clone https://github.com/devlocalhost/sysmon
```

Navigate to the Sysmon directory:
```sh
cd sysmon
```

If Sysmon isn't executable, make it so:
```sh
chmod +x sysmon
```

Finally, run Sysmon:
```sh
./sysmon
```

To use Sysmon anywhere, you can create a symlink:
```sh
echo $(pwd)/sysmon | sudo tee /usr/local/bin/sysmon && sudo chmod +x /usr/local/bin/sysmon
```
This command will echo the current working directory + `/sysmon`, create a new file named `sysmon` in `/usr/local/bin` with executable permissions. If `/usr/local/bin` is in your PATH, then typing `sysmon` anywhere will execute Sysmon.

## Help and Usage
Run `sysmon --help` to display the help menu.

## Usage in Other Scripts
Please refer to the [documentation](DOCS.md).

## Reporting Bugs, Suggestions, or Corrections
Please open an issue, including the traceback and log file (`sysmon -d`). A file named "sysmon.log" will be created in the current directory.

If you want to suggest a new feature or report incorrect data (e.g., CPU temperature or RAM usage), feel free to open an issue.

## Credits
Many thanks to [skyblueborb](https://github.com/skyblueborb) for helping to test, fix, and improve the CPU temperature feature.

Also, many thanks to [ari](https://ari-web.xyz/gh) for assistance with padding and text formatting.
