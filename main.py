import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
import os
from datetime import datetime, timedelta
import csv
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('BOT_TOKEN')
BEEG_USER_ID = int(os.getenv('BEEG_USER_ID'))  # Replace with Beeg's actual user ID
DESTINATION_CHANNEL_NAME = 'general'  # Channel name to send messages to
SUMMON_INTERVAL_HOURS = 3 # How often to summon when offline

# Do not disturb hours configuration (24-hour format)
DO_NOT_DISTURB_START_HOUR = 0   # Midnight (0)
DO_NOT_DISTURB_END_HOUR = 7     # 7 AM

# File paths for data persistence
MESSAGES_FILE = 'summoning_messages.json'
USED_MESSAGES_FILE = 'used_messages.json'
BOT_DATA_FILE = 'bot_data.json'

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='/', intents=intents)

class BeegSummoningBot:
    def __init__(self):
        self.summoning_messages = []
        self.used_messages = set()
        self.last_message_time = None
        self.beeg_offline_since = None
        self.beeg_current_status = None
        self.summoning_task = None
        self.load_data()
    
    def is_do_not_disturb_time(self):
        """Check if current time is within do-not-disturb hours"""
        current_hour = datetime.now().hour
        
        if DO_NOT_DISTURB_START_HOUR <= DO_NOT_DISTURB_END_HOUR:
            # Normal case: e.g., 22:00 to 06:00 (doesn't cross midnight)
            return DO_NOT_DISTURB_START_HOUR <= current_hour < DO_NOT_DISTURB_END_HOUR
        else:
            # Crosses midnight: e.g., 22:00 to 06:00
            return current_hour >= DO_NOT_DISTURB_START_HOUR or current_hour < DO_NOT_DISTURB_END_HOUR
    
    def get_next_allowed_summon_time(self):
        """Get the next time when summoning is allowed"""
        now = datetime.now()
        current_hour = now.hour
        
        if not self.is_do_not_disturb_time():
            return now  # Can send now
        
        # Calculate next allowed time
        if DO_NOT_DISTURB_START_HOUR <= DO_NOT_DISTURB_END_HOUR:
            # Simple case: disturbance period doesn't cross midnight
            next_allowed = now.replace(hour=DO_NOT_DISTURB_END_HOUR, minute=0, second=0, microsecond=0)
            if next_allowed <= now:
                next_allowed += timedelta(days=1)
        else:
            # Crosses midnight
            if current_hour >= DO_NOT_DISTURB_START_HOUR:
                # Currently in the late night portion, wait until morning
                next_allowed = now.replace(hour=DO_NOT_DISTURB_END_HOUR, minute=0, second=0, microsecond=0)
                if next_allowed <= now:
                    next_allowed += timedelta(days=1)
            else:
                # Currently in the early morning portion, wait until end time today
                next_allowed = now.replace(hour=DO_NOT_DISTURB_END_HOUR, minute=0, second=0, microsecond=0)
        
        return next_allowed
    
    def load_summoning_messages_from_csv(self):
        """Load messages from CSV files (phrases and haikus)"""
        messages = []
        
        # Load regular phrases (assuming you have the CSV file)
        try:
            with open('beeg_summoning_phrases.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    messages.append({
                        'id': int(row['number']),
                        'text': row['phrase'],
                        'type': 'phrase'
                    })
        except FileNotFoundError:
            print("beeg_summoning_phrases.csv not found, using fallback messages")
        
        # Load haikus
        try:
            with open('beeg_summoning_haikus.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    messages.append({
                        'id': int(row['number']),
                        'text': row['haiku'].replace(' / ', '\n'),  # Format haiku properly
                        'type': 'haiku'
                    })
        except FileNotFoundError:
            print("beeg_summoning_haikus.csv not found, using fallback messages")
        
        # Fallback messages if CSV files aren't available
        if not messages:
            messages = [
                {'id': 1, 'text': f'🔮 <@{BEEG_USER_ID}> SUMMONING CIRCLE ACTIVATED 🔮', 'type': 'phrase'},
                {'id': 2, 'text': 'Breaking news: Local man spotted in Discord for first time in 3 days', 'type': 'phrase'},
                {'id': 3, 'text': f'<@{BEEG_USER_ID}> has vanished\nLike morning mist with girlfriend\nDiscord grows silent', 'type': 'haiku'},
                {'id': 4, 'text': f'Emergency: Need <@{BEEG_USER_ID}>\'s opinion on literally anything right now', 'type': 'phrase'},
                {'id': 5, 'text': f'Last seen three months ago\nHis profile pic still smiles\nBut <@{BEEG_USER_ID}> is absent', 'type': 'haiku'}
            ]
        
        return messages
    
    def load_data(self):
        """Load all persistent data"""
        # Load summoning messages
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                self.summoning_messages = json.load(f)
        else:
            self.summoning_messages = self.load_summoning_messages_from_csv()
            self.save_messages()
        
        # Load used messages
        if os.path.exists(USED_MESSAGES_FILE):
            with open(USED_MESSAGES_FILE, 'r') as f:
                used_data = json.load(f)
                self.used_messages = set(used_data.get('used_ids', []))
        
        # Load bot data
        if os.path.exists(BOT_DATA_FILE):
            with open(BOT_DATA_FILE, 'r') as f:
                bot_data = json.load(f)
                last_time_str = bot_data.get('last_message_time')
                if last_time_str:
                    self.last_message_time = datetime.fromisoformat(last_time_str)
                
                offline_since_str = bot_data.get('beeg_offline_since')
                if offline_since_str:
                    self.beeg_offline_since = datetime.fromisoformat(offline_since_str)
                
                self.beeg_current_status = bot_data.get('beeg_current_status')
    
    def save_messages(self):
        """Save summoning messages to file"""
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.summoning_messages, f, indent=2, ensure_ascii=False)
    
    def save_used_messages(self):
        """Save used messages to file"""
        with open(USED_MESSAGES_FILE, 'w') as f:
            json.dump({'used_ids': list(self.used_messages)}, f, indent=2)
    
    def save_bot_data(self):
        """Save bot data to file"""
        data = {
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'beeg_offline_since': self.beeg_offline_since.isoformat() if self.beeg_offline_since else None,
            'beeg_current_status': self.beeg_current_status
        }
        with open(BOT_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_random_message(self):
        """Get a random unused message, reset if all used"""
        available_messages = [msg for msg in self.summoning_messages 
                            if msg['id'] not in self.used_messages]
        
        # If all messages have been used, reset the used set
        if not available_messages:
            self.used_messages.clear()
            available_messages = self.summoning_messages
            print("All messages used! Resetting used messages list.")
        
        message = random.choice(available_messages)
        self.used_messages.add(message['id'])
        self.save_used_messages()
        
        return message
    
    def get_user_status(self, user_id):
        """Get the current status of a user"""
        user = bot.get_user(user_id)
        if user is None:
            return 'unknown'
        
        # Check all guilds the bot is in for the user's presence
        for guild in bot.guilds:
            member = guild.get_member(user_id)
            if member:
                if member.status == discord.Status.offline:
                    return 'offline'
                elif member.status == discord.Status.online:
                    return 'online'
                elif member.status == discord.Status.idle:
                    return 'idle'
                elif member.status == discord.Status.dnd:
                    return 'dnd'
        return 'offline'  # Default to offline if not found
    
    async def on_beeg_status_change(self, old_status, new_status):
        """Handle Beeg's status changes"""
        print(f"Beeg status changed: {old_status} -> {new_status}")
        
        self.beeg_current_status = new_status
        current_time = datetime.now()
        
        if new_status == 'offline' and old_status != 'offline':
            # Beeg just went offline
            self.beeg_offline_since = current_time
            print(f"Beeg went offline at {current_time}. Starting summoning countdown...")
            await self.start_summoning_cycle()
            
        elif new_status != 'offline' and old_status == 'offline':
            # Beeg came online
            self.beeg_offline_since = None
            print(f"Beeg came online! Stopping summoning cycle.")
            await self.stop_summoning_cycle()
        
        self.save_bot_data()
    
    async def start_summoning_cycle(self):
        """Start the summoning cycle for offline Beeg"""
        if self.summoning_task:
            self.summoning_task.cancel()
        
        # Create a new task that will summon every X hours while Beeg is offline
        self.summoning_task = asyncio.create_task(self.summoning_loop())
    
    async def stop_summoning_cycle(self):
        """Stop the summoning cycle"""
        if self.summoning_task:
            self.summoning_task.cancel()
            self.summoning_task = None
    
    async def summoning_loop(self):
        """Loop that sends summoning messages while Beeg is offline"""
        try:
            # Wait for the interval before first summon
            await asyncio.sleep(SUMMON_INTERVAL_HOURS * 3600)
            
            while self.beeg_current_status == 'offline':
                # Check if it's do-not-disturb time
                if self.is_do_not_disturb_time():
                    next_allowed = self.get_next_allowed_summon_time()
                    wait_seconds = (next_allowed - datetime.now()).total_seconds()
                    print(f"Do-not-disturb time active. Waiting {wait_seconds/3600:.1f} hours until {next_allowed.strftime('%H:%M')} to summon.")
                    await asyncio.sleep(wait_seconds)
                    continue
                
                await self.send_summoning_message()
                await asyncio.sleep(SUMMON_INTERVAL_HOURS * 3600)
                
        except asyncio.CancelledError:
            print("Summoning loop cancelled (Beeg came online or bot stopping)")
    
    async def send_summoning_message(self):
        """Send a random summoning message to the general channel"""
        # Double-check that Beeg is still offline
        current_status = self.get_user_status(BEEG_USER_ID)
        if current_status != 'offline':
            print("Beeg is no longer offline, stopping summons")
            await self.stop_summoning_cycle()
            return
        
        # Double-check do-not-disturb time
        if self.is_do_not_disturb_time():
            print("Attempted to send message during do-not-disturb hours, skipping")
            return
        
        # Find the general channel in any guild
        general_channel = None
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.name.lower() == DESTINATION_CHANNEL_NAME:
                    general_channel = channel
                    break
            if general_channel:
                break
        
        if not general_channel:
            print(f"Could not find #{DESTINATION_CHANNEL_NAME} channel in any guild")
            return
        
        message_data = self.get_random_message()
        message_text = message_data['text']
        
        # Calculate how long Beeg has been offline
        offline_duration = ""
        if self.beeg_offline_since:
            delta = datetime.now() - self.beeg_offline_since
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            if hours > 0:
                offline_duration = f"\n⏰ *<@{BEEG_USER_ID}> has been offline for {hours}h {minutes}m*"
            else:
                offline_duration = f"\n⏰ *<@{BEEG_USER_ID}> has been offline for {minutes}m*"
        
        # Add some flair based on message type
        if message_data['type'] == 'haiku':
            formatted_message = f"🎋 **Auto-Haiku #{message_data['id']}** 🎋\n```\n{message_text}\n```"
        else:
            formatted_message = f"📢 **Auto-Summon #{message_data['id']}** 📢\n{message_text}"
        
        try:
            await general_channel.send(formatted_message)
            self.last_message_time = datetime.now()
            self.save_bot_data()
            print(f"Sent summoning message #{message_data['id']} to #{general_channel.name}")
        except discord.errors.Forbidden:
            print(f"No permission to send messages in #{general_channel.name}")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def check_initial_beeg_status(self):
        """Check Beeg's status when bot starts up"""
        current_status = self.get_user_status(BEEG_USER_ID)
        print(f"Initial Beeg status: {current_status}")
        
        # If we don't have a previous status, set it
        if self.beeg_current_status is None:
            self.beeg_current_status = current_status
        
        # If Beeg was offline when bot shut down and is still offline, resume summoning
        if current_status == 'offline' and self.beeg_offline_since:
            print("Beeg is still offline from before bot restart. Resuming summoning cycle...")
            await self.start_summoning_cycle()
        elif current_status == 'offline' and self.beeg_offline_since is None:
            # Beeg is offline but we don't have an offline timestamp, set it now
            self.beeg_offline_since = datetime.now()
            await self.start_summoning_cycle()
        elif current_status != 'offline':
            # Beeg is online, make sure we're not summoning
            self.beeg_offline_since = None
            await self.stop_summoning_cycle()
        
        self.beeg_current_status = current_status
        self.save_bot_data()

# Initialize the summoning bot
summoning_bot = BeegSummoningBot()

@bot.event
async def on_ready():
    print(f'Current time: {datetime.now()}')
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    print(f'Do-not-disturb hours: {DO_NOT_DISTURB_START_HOUR:02d}:00 to {DO_NOT_DISTURB_END_HOUR:02d}:00')
    
    # Check Beeg's initial status and start summoning if needed
    await summoning_bot.check_initial_beeg_status()

@bot.event
async def on_presence_update(before, after):
    """Detect when Beeg's status changes"""
    if after.id == BEEG_USER_ID:
        old_status = 'offline' if before.status == discord.Status.offline else 'online'
        new_status = 'offline' if after.status == discord.Status.offline else 'online'
        
        # Only trigger if status actually changed
        if old_status != new_status:
            await summoning_bot.on_beeg_status_change(old_status, new_status)

# Helper function for cleanup commands
async def delete_bot_messages_except_latest(channel, limit=None):
    """Delete all bot messages except the most recent one"""
    bot_messages = []
    
    # Collect bot messages
    async for message in channel.history(limit=limit):
        if message.author == bot.user:
            bot_messages.append(message)
    
    # Sort by timestamp (newest first) and skip the first one
    bot_messages.sort(key=lambda m: m.created_at, reverse=True)
    messages_to_delete = bot_messages[1:]  # Skip the newest message
    
    deleted_count = 0
    for message in messages_to_delete:
        try:
            await message.delete()
            deleted_count += 1
            await asyncio.sleep(0.5)  # Rate limiting
        except discord.errors.NotFound:
            pass  # Message already deleted
        except Exception as e:
            print(f"Error deleting message: {e}")
    
    return deleted_count

# Fix 1: Update the manual summon command (replace the existing command)
@bot.command(name='summon')
async def summon_command(ctx, user: discord.Member = None):
    """Manual summon command: /summon @username"""
    if user is None:
        # Default to Beeg if no user specified
        user = bot.get_user(BEEG_USER_ID)
        if user is None:
            await ctx.send("❌ Could not find the target user!")
            return
    
    # Check if it's do-not-disturb time for automatic summons
    if summoning_bot.is_do_not_disturb_time():
        next_allowed = summoning_bot.get_next_allowed_summon_time()
        await ctx.send(f"🌙 **Do-not-disturb time active!**\n"
                      f"⏰ Quiet hours: {DO_NOT_DISTURB_START_HOUR:02d}:00 - {DO_NOT_DISTURB_END_HOUR:02d}:00\n"
                      f"🔔 Next summon allowed at: {next_allowed.strftime('%H:%M')}\n"
                      f"💡 *Manual summons still work during quiet hours*")
    
    # Get a random summoning message
    message_data = summoning_bot.get_random_message()
    message_text = message_data['text']
    
    # Replace any existing mentions in the message with the target user
    # This handles cases where CSV has Beeg's ID but we want to summon someone else
    import re
    mention_pattern = r'<@\d+>'
    message_text = re.sub(mention_pattern, user.mention, message_text)
    
    # Format the message
    if message_data['type'] == 'haiku':
        formatted_message = (f"🎋 **MANUAL SUMMONING HAIKU #{message_data['id']}** 🎋\n"
                           f"```\n{message_text}\n```")
    else:
        formatted_message = (f"📢 **MANUAL SUMMONING #{message_data['id']}** 📢\n"
                           f"{message_text}")
    
    await ctx.send(formatted_message)
    print(f"Manual summon used by {ctx.author} targeting {user.display_name}")

@bot.command(name='cleanup')
async def cleanup_bot_messages(ctx, limit: int = 10):
    """Delete the bot's recent messages except the latest one (default: last 10 messages)"""
    if limit > 50:
        await ctx.send("❌ Limit too high! Maximum 50 messages at once.")
        return
    
    try:
        deleted_count = await delete_bot_messages_except_latest(ctx.channel, limit=100)
        
        if deleted_count > 0:
            # Send confirmation (this will auto-delete after 5 seconds)
            confirmation = await ctx.send(f"🗑️ Deleted {deleted_count} bot messages (kept the latest one)!")
            await asyncio.sleep(5)
            await confirmation.delete()
        else:
            await ctx.send("ℹ️ No bot messages found to delete.")
        
        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # Message already deleted
        except Exception as e:
            print(f"Error deleting command message: {e}")
            
    except discord.errors.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to delete messages in this channel.")
    except Exception as e:
        await ctx.send(f"❌ Error deleting messages: {e}")

@bot.command(name='cleanup_all')
async def cleanup_all_bot_messages(ctx):
    """Delete ALL bot messages except the latest one in this channel (use with caution!)"""
    try:
        # Confirm before mass deletion
        confirm_msg = await ctx.send("⚠️ This will delete ALL bot messages except the latest one in this channel. React with ✅ to confirm (30 second timeout)")
        await confirm_msg.add_reaction("✅")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirm_msg.id
        
        try:
            await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.edit(content="❌ Cleanup cancelled (timeout)")
            return
        
        await confirm_msg.delete()
        
        # Delete all bot messages except the latest one
        deleted_count = await delete_bot_messages_except_latest(ctx.channel)
        
        # Send final confirmation
        final_msg = await ctx.send(f"🗑️ Cleanup complete! Deleted {deleted_count} bot messages (kept the latest one).")
        await asyncio.sleep(5)
        await final_msg.delete()
        
        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # Message already deleted
        except Exception as e:
            print(f"Error deleting command message: {e}")
        
    except discord.errors.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to delete messages in this channel.")
    except Exception as e:
        await ctx.send(f"❌ Error during cleanup: {e}")

# Fix 2: Add command to reload messages from CSV (add this new command)
@bot.command(name='reload_messages')
@commands.has_permissions(administrator=True)
async def reload_messages(ctx):
    """Reload summoning messages from CSV files (admin only)"""
    try:
        # Force reload from CSV
        summoning_bot.summoning_messages = summoning_bot.load_summoning_messages_from_csv()
        summoning_bot.save_messages()  # Save the new messages to JSON
        summoning_bot.used_messages.clear()  # Reset used messages since we have new content
        summoning_bot.save_used_messages()
        
        total_messages = len(summoning_bot.summoning_messages)
        phrases = len([m for m in summoning_bot.summoning_messages if m['type'] == 'phrase'])
        haikus = len([m for m in summoning_bot.summoning_messages if m['type'] == 'haiku'])
        
        await ctx.send(f"✅ **Messages reloaded from CSV files!**\n"
                      f"📝 Total: {total_messages} ({phrases} phrases, {haikus} haikus)\n"
                      f"🔄 Used message list reset")
        
        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass
        
    except Exception as e:
        await ctx.send(f"❌ **Error reloading messages:** {e}")

# Fix 3: Add command to delete the JSON file and force CSV reload (add this new command)
@bot.command(name='force_csv_reload')
@commands.has_permissions(administrator=True)
async def force_csv_reload(ctx):
    """Delete JSON cache and force reload from CSV files (admin only)"""
    try:
        # Delete the JSON files to force fresh load
        if os.path.exists(MESSAGES_FILE):
            os.remove(MESSAGES_FILE)
        if os.path.exists(USED_MESSAGES_FILE):
            os.remove(USED_MESSAGES_FILE)
        
        # Reload everything
        summoning_bot.summoning_messages = summoning_bot.load_summoning_messages_from_csv()
        summoning_bot.save_messages()
        summoning_bot.used_messages.clear()
        summoning_bot.save_used_messages()
        
        total_messages = len(summoning_bot.summoning_messages)
        phrases = len([m for m in summoning_bot.summoning_messages if m['type'] == 'phrase'])
        haikus = len([m for m in summoning_bot.summoning_messages if m['type'] == 'haiku'])
        
        await ctx.send(f"✅ **Forced fresh reload from CSV files!**\n"
                      f"📝 Total: {total_messages} ({phrases} phrases, {haikus} haikus)\n"
                      f"🗑️ Deleted old cache files\n"
                      f"🔄 Used message list reset")
        
        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass
        
    except Exception as e:
        await ctx.send(f"❌ **Error during force reload:** {e}")

# Fix 4: Add debug command to see what messages are loaded (add this new command)
@bot.command(name='debug_messages')
@commands.has_permissions(administrator=True)
async def debug_messages(ctx):
    """Show sample of loaded messages for debugging (admin only)"""
    if not summoning_bot.summoning_messages:
        await ctx.send("❌ No messages loaded!")
        return
    
    # Show first 3 messages as examples
    sample_messages = summoning_bot.summoning_messages[:3]
    debug_text = "🔍 **Debug: Sample loaded messages**\n"
    
    for msg in sample_messages:
        debug_text += f"\n**ID {msg['id']} ({msg['type']}):**\n"
        debug_text += f"```{msg['text'][:100]}{'...' if len(msg['text']) > 100 else ''}```"
    
    await ctx.send(debug_text)

@bot.command(name='summon_stats')
async def summon_stats(ctx):
    """Show summoning statistics"""
    total_messages = len(summoning_bot.summoning_messages)
    used_messages = len(summoning_bot.used_messages)
    remaining = total_messages - used_messages
    
    phrases = len([m for m in summoning_bot.summoning_messages if m['type'] == 'phrase'])
    haikus = len([m for m in summoning_bot.summoning_messages if m['type'] == 'haiku'])
    
    last_time = summoning_bot.last_message_time
    last_time_str = last_time.strftime("%Y-%m-%d %H:%M:%S") if last_time else "Never"
    
    # Do-not-disturb status
    dnd_status = "🌙 ACTIVE" if summoning_bot.is_do_not_disturb_time() else "☀️ INACTIVE"
    
    stats_message = (f"📊 **Beeg Summoning Stats** 📊\n"
                    f"📝 Total messages: {total_messages} ({phrases} phrases, {haikus} haikus)\n"
                    f"✅ Used messages: {used_messages}\n"
                    f"⏳ Remaining: {remaining}\n"
                    f"🕐 Last auto-summon: {last_time_str}\n"
                    f"🔕 Do-not-disturb ({DO_NOT_DISTURB_START_HOUR:02d}:00-{DO_NOT_DISTURB_END_HOUR:02d}:00): {dnd_status}")
    
    await ctx.send(stats_message)

@bot.command(name='reset_summons')
@commands.has_permissions(administrator=True)
async def reset_summons(ctx):
    """Reset the used messages list (admin only)"""
    summoning_bot.used_messages.clear()
    summoning_bot.save_used_messages()
    await ctx.send("🔄 **Summoning messages reset!** All messages are now available again.")
    
    # Delete the user's command message
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass

@bot.command(name='beeg_status')
async def beeg_status(ctx):
    """Check if Beeg is online or offline"""
    user = bot.get_user(BEEG_USER_ID)
    if user is None:
        await ctx.send("❌ Could not find Beeg!")
        return
    
    current_status = summoning_bot.get_user_status(BEEG_USER_ID)
    
    # Status emoji and text
    if current_status == 'offline':
        status_emoji = "💤"
        status_text = "OFFLINE (prime summoning time!)"
    elif current_status == 'online':
        status_emoji = "✅"
        status_text = "ONLINE (summoning successful!)"
    elif current_status == 'idle':
        status_emoji = "🌙"
        status_text = "IDLE (maybe summoning will work?)"
    elif current_status == 'dnd':
        status_emoji = "🔴"
        status_text = "DO NOT DISTURB (summoning may anger the Beeg)"
    else:
        status_emoji = "❓"
        status_text = "UNKNOWN (Schrödinger's Beeg)"
    
    # Add offline duration if applicable
    offline_info = ""
    if current_status == 'offline' and summoning_bot.beeg_offline_since:
        delta = datetime.now() - summoning_bot.beeg_offline_since
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        if hours > 0:
            offline_info = f"\n⏰ Offline for: {hours}h {minutes}m"
        else:
            offline_info = f"\n⏰ Offline for: {minutes}m"
        
        # Add summoning status
        if summoning_bot.summoning_task and not summoning_bot.summoning_task.done():
            offline_info += "\n🔮 Auto-summoning: ACTIVE"
        else:
            offline_info += "\n🔮 Auto-summoning: INACTIVE"
    
    # Add do-not-disturb status
    dnd_info = ""
    if summoning_bot.is_do_not_disturb_time():
        next_allowed = summoning_bot.get_next_allowed_summon_time()
        dnd_info = f"\n🌙 Do-not-disturb active until {next_allowed.strftime('%H:%M')}"
    
    await ctx.send(f"{status_emoji} **Beeg is currently: {status_text}**{offline_info}{dnd_info}")

@bot.command(name='force_summon_check')
@commands.has_permissions(administrator=True)
async def force_summon_check(ctx):
    """Force check Beeg's status and restart summoning if needed (admin only)"""
    old_status = summoning_bot.beeg_current_status
    await summoning_bot.check_initial_beeg_status()
    new_status = summoning_bot.beeg_current_status
    
    await ctx.send(f"🔍 **Status check complete!**\n"
                   f"Previous: {old_status}\n"
                   f"Current: {new_status}\n"
                   f"Summoning active: {summoning_bot.summoning_task is not None and not summoning_bot.summoning_task.done()}")
    
    # Delete the user's command message
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass

@bot.command(name='stop_summoning')
@commands.has_permissions(administrator=True)
async def stop_summoning(ctx):
    """Stop automatic summoning (admin only)"""
    await summoning_bot.stop_summoning_cycle()
    await ctx.send("🛑 **Automatic summoning stopped!** Beeg is safe... for now.")
    
    # Delete the user's command message
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass

@bot.command(name='dnd_status')
async def dnd_status(ctx):
    """Check current do-not-disturb status"""
    current_time = datetime.now()
    is_dnd = summoning_bot.is_do_not_disturb_time()
    
    if is_dnd:
        next_allowed = summoning_bot.get_next_allowed_summon_time()
        time_remaining = next_allowed - current_time
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        
        await ctx.send(f"🌙 **Do-not-disturb is ACTIVE**\n"
                      f"⏰ Quiet hours: {DO_NOT_DISTURB_START_HOUR:02d}:00 - {DO_NOT_DISTURB_END_HOUR:02d}:00\n"
                      f"🔔 Next summon allowed: {next_allowed.strftime('%H:%M')}\n"
                      f"⏳ Time remaining: {hours}h {minutes}m")
    else:
        await ctx.send(f"☀️ **Do-not-disturb is INACTIVE**\n"
                      f"⏰ Quiet hours: {DO_NOT_DISTURB_START_HOUR:02d}:00 - {DO_NOT_DISTURB_END_HOUR:02d}:00\n"
                      f"✅ Auto-summoning is allowed right now!")

if __name__ == "__main__":
    # Make sure to replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token
    if DISCORD_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your Discord bot token in the DISCORD_TOKEN variable!")
        print("You can get a token by creating a bot at https://discord.com/developers/applications")
    else:
        bot.run(DISCORD_TOKEN)