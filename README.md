# Telegram Security Bot

Telegram group moderation bot with admin-controlled URL blocking, keyword alerts, and EVM address detection.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:TELEGRAM_BOT_TOKEN = "<telegram-bot-token>"
telegram-security-bot
```

The bot stores group settings in `data/security-bot.json` by default. Override it with `SECURITY_BOT_DATA` or `--data-file`.

## Railway

This repository includes `railway.json` with the start command Railway needs:

```sh
PYTHONPATH=src python -m security_bot.bot
```

Configure these Railway variables on the bot service:

```sh
TELEGRAM_BOT_TOKEN=<telegram-bot-token>
SECURITY_BOT_DATA=/app/data/security-bot.json
LOG_LEVEL=WARNING
SECURITY_BOT_NAME_SCAN_SECONDS=60
```

Attach a Railway volume to the service at `/app/data` so group settings survive deploys and restarts. Keep the service at one replica because the JSON settings store is local to one running process.

If this token previously used a webhook, clear it before using polling:

```sh
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/deleteWebhook?drop_pending_updates=true
```

## Telegram Permissions

Add the bot to your group as an admin. It needs permission to delete messages and ban users.

If the bot does not receive regular group messages after being made admin, check BotFather privacy settings and re-add the bot to the group.

For private alerts, each recipient must open the bot in Telegram and send `/start` once. Telegram does not let bots initiate private chats with users who have never started them.

## Security Notes

- Store the Telegram token only in Railway variables or local environment variables. Do not commit `.env` files or real tokens.
- URL moderation scans visible message text, captions, Telegram URL entities, and hidden `text_link` URLs.
- Polling mode has no public HTTP endpoint, so there is no webhook secret to configure.
- The JSON settings file stores group configuration, known user names, recipient usernames, and recipient Telegram IDs. Treat the Railway volume as private operational data.
- This upstream repository does not include a license file. Get permission before commercial or public production use if you do not control the code.

## Admin Commands

- `/url ON|OFF` enables or disables URL restriction. Default: OFF.
- `/addurl example.com` allows a domain and its subdomains.
- `/listurl` lists allowed URL domains.
- `/delurl example.com` removes an allowed domain.
- `/alert ON|OFF` enables or disables keyword alerts. Default: OFF.
- `/addreceiver @username` adds an alert recipient.
- `/listreceiver` lists alert recipients.
- `/delreceiver @username` removes an alert recipient.
- `/addkeyword Meta` adds a watched keyword.
- `/listkeyword` lists watched keywords.
- `/delkeyword Meta` removes a watched keyword.
- `/scandelacc` scans known group members and removes deleted Telegram accounts.
- `/delca ON|OFF` removes users when they join with an EVM-like address in their displayed name. Default: OFF.
- `/sendca ON|OFF` deletes messages containing EVM-like addresses. Default: OFF.
- `/warningmsg ON|OFF` enables or disables scheduled warning messages. Default: OFF.
- `/warningtxt message` sets the warning message text.
- `/warningfreq seconds` sets how often the warning is sent. Default: 600 seconds. Minimum: 60 seconds.
- `/warnmedia` adds media to warning messages by replying to an image, GIF, or video.

Group admins are always allowed to send URLs. Only group admins can change bot settings.

Keyword alerts trigger on joins, on messages from a user whose display name changed, and on a periodic scan of users the bot has already seen in the group. The scan interval defaults to 60 seconds and can be changed with `SECURITY_BOT_NAME_SCAN_SECONDS`.

`/scandelacc` can only scan users the bot already knows from joins or messages. Telegram Bot API does not provide bots with a full group member list.

For `/warnmedia`, first send the image, GIF, or video in the group, then reply to that media message with `/warnmedia`. Telegram file IDs are stored, not downloaded media files.
