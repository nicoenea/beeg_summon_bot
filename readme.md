# 🔮 Beeg Summoning Bot

A Discord bot designed to automatically summon your absent friends (specifically Beeg) back to the server when they've disappeared into the girlfriend dimension.

## 📖 Overview

This bot tracks when a specific user goes offline and automatically sends hilarious summoning messages every 3 hours until they return. It includes 1000+ custom phrases and 500+ haikus designed to guilt trip your friend back into Discord.

## ✨ Features

### 🤖 Automatic Summoning

- **Event-driven status tracking** - Instantly detects when target user goes offline/online
- **Smart timing** - Only starts summoning when user goes offline
- **Persistent tracking** - Remembers offline duration across bot restarts
- **No message repetition** - Cycles through all messages before repeating

### 💬 Message Content

- **1000 summoning phrases** - Ranging from gentle to dramatically ridiculous
- **500 haikus** - Poetic guilt trips in traditional 5-7-5 format
- **Auto-tagging** - All messages properly mention the target user
- **Offline duration display** - Shows how long the user has been gone

### 🎮 Commands

- `/summon [@user]` - Manually summon any user (defaults to target)
- `/beeg_status` - Check target user's current status and offline duration
- `/summon_stats` - View message statistics and usage
- `/cleanup [limit]` - Delete bot messages (default: 10)
- `/cleanup_all` - Delete ALL bot messages (with confirmation)

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
- A Discord bot token

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd beeg-summoning-bot
   ```

2. **Install dependencies**

   ```bash
   pip install discord.py
   ```

3. **Create your Discord bot**

   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application → Bot → Copy token
   - Enable these intents: Message Content, Server Members, Presence

4. **Configure the bot**

   - Open `main.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token
   - Set `BEEG_USER_ID` to your target user's Discord ID
   - Adjust `DESTINATION_CHANNEL_NAME` if needed (default: 'general')

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
3. **After 3 hours offline** → Sends first summoning message
4. **Every 3 hours** → Sends another message (different each time)
5. **User comes online** → Bot immediately stops summoning
6. **Cycle repeats** whenever user goes offline again

## 🛠️ Configuration

### Key Settings (in `main.py`)

```python
BEEG_USER_ID = os.getenv('USER_ID')      # Target user's Discord ID
DESTINATION_CHANNEL_NAME = 'general'    # Channel to send messages
SUMMON_INTERVAL_HOURS = 3               # Hours between messages
```

### Getting User ID

1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click target user → Copy User ID

## 📝 CSV File Format

### Phrases (`beeg_summoning_phrases.csv`)

```csv
number,phrase
1,"🔮 <@USER_ID> SUMMONING CIRCLE ACTIVATED 🔮"
2,"Breaking news: Local man spotted in Discord for first time in 3 days"
```

### Haikus (`beeg_summoning_haikus.csv`)

```csv
number,haiku
1001,"<@USER_ID> has vanished / Like morning mist with girlfriend / Discord grows silent"
1002,"Last seen three months ago / His profile pic still smiles / But <@USER_ID> is absent"
```

**Note:** Use `<@USER_ID>` in your CSV files for proper Discord mentions.

## 🎨 Message Examples

### Automatic Messages

```
📢 Auto-Summon #42 📢
⏰ @Beeg has been offline for 5h 23m
Emergency: Need @Beeg's opinion on literally anything right now
```

### Haiku Messages

```
🎋 Auto-Haiku #1337 🎋
⏰ @Beeg has been offline for 2h 15m
```

```
@Beeg has vanished
Like morning mist with girlfriend
Discord grows silent
```

## 🔒 Permissions

The bot needs these Discord permissions:

- **Send Messages** - To send summoning messages
- **Manage Messages** - To delete its own messages (for cleanup commands)
- **Read Message History** - To find messages to delete
- **Use Slash Commands** - For command functionality

## 🐛 Troubleshooting

### Common Issues

**Bot uses fallback messages instead of CSV**

- Run `/force_csv_reload` to refresh from CSV files
- Check that CSV files are in the same directory as `main.py`
- Verify CSV format matches examples above

**Manual summon shows raw text instead of mentions**

- Ensure CSV files use `<@USER_ID>` format for mentions
- Run `/debug_messages` to see loaded message format
- User ID should be numbers only (no @ symbol in CSV)

**Bot doesn't detect status changes**

- Verify bot has Presence intent enabled
- Check that bot is in same server as target user
- Use `/force_summon_check` to manually refresh status

**Permission errors**

- Ensure bot has required permissions in target channel
- Check bot role hierarchy in server settings

### Reset Everything

If something goes wrong, delete these files and restart:

- `summoning_messages.json`
- `used_messages.json`
- `bot_data.json`

## 🤝 Contributing

Feel free to:

- Add more creative summoning messages
- Improve the haiku collection
- Submit bug fixes or feature requests
- Share your own bot customizations

## ⚠️ Disclaimer

This bot is designed for fun among friends. Please:

- Use responsibly and respect your friends' boundaries
- Don't spam excessively or harass users
- Consider the target user's schedule and time zones
- Remember that some people need breaks from Discord

## 📜 License

This project is open source. Use it, modify it, and share it with friends who have also disappeared into relationship bliss.

---

_"In a world where friends vanish into the girlfriend dimension, one bot stands guard over Discord servers everywhere..."_ 🎭
