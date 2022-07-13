# XenPoster

XenPoster - A tool to post to XenForo forums from the command line

Version 0.3.1

## Usage

```bash
kuantum@battlestation:~$ python3 /mnt/c/Users/mrsam/Documents/Projects/xenposter/xenposter/xenposter.py -h
usage: xenposter.py [-h] -u USERNAME -p PASSWORD [-l] [--post] [--react REACT] [-c] [-f] [-r] [-t TOTP]
                    [--timeout TIMEOUT] [-e EMOTE] [--remote-site REMOTE_SITE] [--remote-port REMOTE_PORT]
                    url

xenposter - XenForo Automation Script

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  url                   The URL of the XenForo forum thread
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        Password

xenforo actions:
  -l, --login           Login to XenForo and do nothing
  --post                Post a message to the XenForo thread
  --react REACT         React to a post in the XenForo thread

browser options:
  -c, --chrome          Use Chrome
  -f, --firefox         Use Firefox
  -r, --remote          Use remote driver

optional arguments:
  -t TOTP, --totp TOTP  TOTP Secret Key, required if you\'ve set up 2FA
  --timeout TIMEOUT     Timeout for the browser
  -e EMOTE, --emote EMOTE
                        Emote to use

remote options:
  --remote-site REMOTE_SITE
                        Remote site to use
  --remote-port REMOTE_PORT
                        Remote port to use
```

## Installation

For use as an executable, look at the Packages.

For use as a module, it is still being actively developed on, but feel free to download `xenposter.py` and import it locally for now.

## Notes

You can use the Remote WebDriver, but it requires `chrome` or `firefox` to be specified.
A typical CLI invocation might look like this:

```bash
xenposter.py "https://www.edgegamers.com/threads/368386/" -r -c -u USERNAME -p PASSWORD -t TOTP_SECRET_KEY -m "R&U" --remote-site "http://192.168.1.100" --remote-port "4444"
```

Selenium uses Drivers, such as ChromeDriver, GeckoDriver, etc. Make sure you download the approriate drivers before using this script.
