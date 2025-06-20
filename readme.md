# 🔮 Beeg Summoning Bot

A Discord bot designed to automatically summon your absent friends (specifically Beeg) back to the server when they've disappeared into the girlfriend dimension.

## 📖 Overview

This bot tracks when a specific user goes offline and automatically sends hilarious summoning messages every 3 hours until they return. It includes 1000+ custom phrases and 500+ haikus designed to guilt trip your friend back into Discord. The bot now features smart do-not-disturb hours, enhanced cleanup commands, and improved message management.

## ✨ Features

### 🤖 Automatic Summoning

- **Event-driven status tracking** - Instantly detects when target user goes offline/online
- **Smart timing** - Only starts summoning when user goes offline
- **Persistent tracking** - Remembers offline duration across bot restarts
- **No message repetition** - Cycles through all messages before repeating
- **🌙 Do-not-disturb hours** - Respects quiet hours (configurable, default: midnight-7AM)
- **Intelligent scheduling** - Delays summoning until allowed hours if needed

### 💬 Message Content

- **1000 summoning phrases** - Ranging from gentle to dramatically ridiculous
- **500 haikus** - Poetic guilt trips in traditional 5-7-5 format
- **Auto-tagging** - All messages properly mention the target user
- **Offline duration display** - Shows how long the user has been gone
- **Smart message formatting** - Different styles for phrases vs haikus
- **Flexible user targeting** - Manual summons can target any user

### 🎮 User Commands

- `/summon [@user]` - Manually summon any user (defaults to target)
- `/beeg_status` - Check target user's current status and offline duration
- `/summon_stats` - View message statistics and usage
- `/cleanup [limit]` - Delete bot messages except the latest (default: 10)
- `/cleanup_all` - Delete ALL bot messages except latest (with confirmation)
- `/dnd_status` - Check current do-not-disturb status and timing

### 🔧 Admin Commands

- `/reload_messages` - Reload messages from CSV files
- `/force_csv_reload` - Delete cache and force fresh CSV load
- `/reset_summons` - Reset used message tracking
- `/force_summon_check` - Manually check user status
- `/stop_summoning` - Emergency stop for automatic summoning
- `/debug_messages` - View sample loaded messages

## 🚀 Setup

### Prerequisites

- Python 3.8+
- `discord.py` library
- `python-dotenv` library
- A Discord bot token

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd beeg-summoning-bot
   ```

2. **Install dependencies**

   ```bash
   pip install discord.py python-dotenv
   ```

3. **Create your Discord bot**

   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application → Bot → Copy token
   - Enable these intents: Message Content, Server Members, Presence

4. **Configure the bot**

   Create a `.env` file in the bot directory:

   ```env
   BOT_TOKEN=your_discord_bot_token_here
   BEEG_USER_ID=target_user_discord_id_here
   ```

   Or edit the configuration directly in `main.py`:

   ```python
   DESTINATION_CHANNEL_NAME = 'general'    # Channel to send messages
   SUMMON_INTERVAL_HOURS = 3               # Hours between messages
   DO_NOT_DISTURB_START_HOUR = 0           # Quiet hours start (24h format)
   DO_NOT_DISTURB_END_HOUR = 7             # Quiet hours end (24h format)
   ```

5. **Prepare message files** (optional)

   - Place `beeg_summoning_phrases.csv` and `beeg_summoning_haikus.csv` in the bot directory
   - Format: CSV with `number,phrase` and `number,haiku` columns
   - The bot includes fallback messages if CSV files are missing

6. **Run the bot**
   ```bash
   python main.py
   ```

## 📁 File Structure

```
beeg-summoning-bot/
├── main.py                          # Main bot script
├── .env                             # Environment variables (create this)
├── beeg_summoning_phrases.csv       # 1000 summoning phrases (optional)
├── beeg_summoning_haikus.csv        # 500 haikus (optional)
├── summoning_messages.json          # Cached messages (auto-generated)
├── used_messages.json               # Used message tracking (auto-generated)
├── bot_data.json                    # Bot state data (auto-generated)
└── README.md                        # This file
```

## 🎯 How It Works

1. **Bot starts** and checks target user's status
2. **User goes offline** → Bot starts 3-hour countdown
3. **After 3 hours offline** → Checks if it's allowed time, then sends first summoning message
4. **Every 3 hours** → Sends another message (different each time)
5. **Do-not-disturb protection** → Delays messages until allowed hours
6. **User comes online** → Bot immediately stops summoning
7. **Cycle repeats** whenever user goes offline again

## 🌙 Do-Not-Disturb Feature

The bot respects quiet hours to avoid sending messages at inappropriate times:

- **Default quiet hours**: Midnight (00:00) to 7:00 AM
- **Configurable timing**: Modify `DO_NOT_DISTURB_START_HOUR` and `DO_NOT_DISTURB_END_HOUR`
- **Smart scheduling**: Messages are delayed until allowed hours, not skipped
- **Manual override**: Manual `/summon` commands work during quiet hours
- **Status checking**: Use `/dnd_status` to see current quiet hour status

### Cross-Midnight Configuration

The do-not-disturb system handles periods that cross midnight:

```python
DO_NOT_DISTURB_START_HOUR = 22  # 10 PM
DO_NOT_DISTURB_END_HOUR = 6     # 6 AM
# This creates a quiet period from 10 PM to 6 AM
```

## 🛠️ Configuration

### Environment Variables (.env file)

```env
BOT_TOKEN=your_discord_bot_token_here
BEEG_USER_ID=123456789012345678
```

### Key Settings (in `main.py`)

```python
DESTINATION_CHANNEL_NAME = 'general'    # Channel to send messages
SUMMON_INTERVAL_HOURS = 3               # Hours between messages
DO_NOT_DISTURB_START_HOUR = 0           # Quiet hours start (24h format)
DO_NOT_DISTURB_END_HOUR = 7             # Quiet hours end (24h format)
```

### Getting User ID

1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click target user → Copy User ID

## 📝 CSV File Format

### Phrases (`beeg_summoning_phrases.csv`)

```csv
number,phrase
1,🔮 <@123456789012345678> SUMMONING CIRCLE ACTIVATED 🔮
2,Breaking news: Local man spotted in Discord for first time in 3 days
3,Emergency: Need <@123456789012345678>'s opinion on literally anything right now
```

### Haikus (`beeg_summoning_haikus.csv`)

```csv
number,haiku
1001,<@123456789012345678> has vanished / Like morning mist with girlfriend / Discord grows silent
1002,Last seen three months ago / His profile pic still smiles / But <@123456789012345678> is absent
1003,Offline for hours / The server feels so empty / Come back to us soon
```

**Important Notes:**

- Use the actual Discord User ID (numbers only) in your CSV files
- Haikus use `/` to separate lines (converted to newlines automatically)
- The bot will substitute user mentions dynamically for manual summons

## 🎨 Message Examples

### Automatic Phrase Messages

```
📢 Auto-Summon #42 📢
🔮 @Beeg SUMMONING CIRCLE ACTIVATED 🔮
⏰ @Beeg has been offline for 5h 23m
```

### Automatic Haiku Messages

```
🎋 Auto-Haiku #1337 🎋
```

```
@Beeg has vanished
Like morning mist with girlfriend
Discord grows silent
```

```
⏰ @Beeg has been offline for 2h 15m
```

### Manual Summon Messages

```
📢 MANUAL SUMMONING #123 📢
Emergency: Need @SomeUser's opinion on literally anything right now
```

### Do-Not-Disturb Notifications

```
🌙 Do-not-disturb time active!
⏰ Quiet hours: 00:00 - 07:00
🔔 Next summon allowed at: 07:00
💡 Manual summons still work during quiet hours
```

## 🧹 Cleanup Features

The bot includes intelligent cleanup commands that preserve the most recent message:

- **`/cleanup [limit]`** - Deletes bot messages in batches (keeps latest)
- **`/cleanup_all`** - Mass deletion with confirmation prompt
- **Smart preservation** - Always keeps the newest bot message
- **Auto-deletion** - Command messages and confirmations self-destruct
- **Rate limiting** - Built-in delays to respect Discord API limits

## 🔒 Permissions

The bot needs these Discord permissions:

- **Send Messages** - To send summoning messages
- **Manage Messages** - To delete its own messages (for cleanup commands)
- **Read Message History** - To find messages to delete
- **Use Slash Commands** - For command functionality
- **View Server Members** - To check user presence

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't load CSV files**

- Run `/force_csv_reload` to refresh from CSV files
- Check that CSV files are in the same directory as `main.py`
- Verify CSV format matches examples above
- Use `/debug_messages` to see what's loaded

**Bot doesn't detect status changes**

- Verify bot has Presence intent enabled in Discord Developer Portal
- Check that bot is in same server as target user
- Use `/force_summon_check` to manually refresh status
- Ensure bot has "View Server Members" permission

**Manual summons don't mention correctly**

- CSV files should use actual Discord User ID numbers
- For manual summons targeting different users, mentions are automatically substituted
- Use `/debug_messages` to verify message format

**Do-not-disturb not working**

- Check `/dnd_status` to see current quiet hour settings
- Verify your timezone matches the bot's server timezone
- Manual summons override quiet hours (this is intentional)

**Permission errors**

- Ensure bot has required permissions in target channel
- Check bot role hierarchy in server settings
- Verify bot can read message history for cleanup commands

### Environment Variable Issues

**Bot token not found**

- Create `.env` file in the same directory as `main.py`
- Ensure `.env` file contains `BOT_TOKEN=your_actual_token`
- Don't commit `.env` file to version control

**User ID not set**

- Add `BEEG_USER_ID=123456789012345678` to `.env` file
- Or set it directly in the code if not using environment variables

### Reset Everything

If something goes wrong, delete these files and restart:

- `summoning_messages.json`
- `used_messages.json`
- `bot_data.json`

The bot will regenerate them with fresh data.

## 🎯 Advanced Usage

### Multiple Target Users

To use the bot with different users:

1. Change `BEEG_USER_ID` in `.env`
2. Update CSV files with new user mentions
3. Run `/force_csv_reload`

### Custom Quiet Hours

For different schedules:

```python
# Night shift schedule (quiet during day)
DO_NOT_DISTURB_START_HOUR = 8   # 8 AM
DO_NOT_DISTURB_END_HOUR = 16    # 4 PM

# Weekend schedule (quiet until noon)
DO_NOT_DISTURB_START_HOUR = 0   # Midnight
DO_NOT_DISTURB_END_HOUR = 12    # Noon
```

### Faster/Slower Summoning

Adjust summoning frequency:

```python
SUMMON_INTERVAL_HOURS = 1    # Very aggressive (every hour)
SUMMON_INTERVAL_HOURS = 6    # More patient (every 6 hours)
SUMMON_INTERVAL_HOURS = 24   # Daily reminder
```

## 🤝 Contributing

Feel free to:

- Add more creative summoning messages
- Improve the haiku collection
- Submit bug fixes or feature requests
- Share your own bot customizations
- Suggest new features like timezone support

## ⚠️ Disclaimer

This bot is designed for fun among friends. Please:

- Use responsibly and respect your friends' boundaries
- Don't spam excessively or harass users
- Consider the target user's schedule and time zones
- Remember that some people need breaks from Discord
- The do-not-disturb feature helps, but use common sense

## 📜 License

This project is open source. Use it, modify it, and share it with friends who have also disappeared into relationship bliss.

---

_"In a world where friends vanish into the girlfriend dimension, one bot stands guard over Discord servers everywhere... but only during appropriate hours."_ 🎭
