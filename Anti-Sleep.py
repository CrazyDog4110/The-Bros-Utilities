import discord 
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import os
import sys
from pytimeparse.timeparse import timeparse
import datetime
from jokeapi import Jokes
from random import choice
import logging
import traceback
import sqlite3
import aiohttp
import re
from urllib.parse import urlparse
from discord import ui

in_app = []

def get_direct_gif_url(tenor_url):
    # Parse the original URL to ensure it's valid
    parsed_url = urlparse(tenor_url)
    
    # Check if the URL is from Tenor
    if 'tenor.com' not in parsed_url.netloc:
        return None  # Not a Tenor URL

    try:
        response = requests.get(tenor_url)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Look for 'media' links in the response text
        start_index = response.text.find('media')
        if start_index != -1:
            # Search for the GIF URL by extracting the link
            end_index = response.text.find('.gif', start_index) + 4  # Add 4 to include '.gif'
            gif_url = response.text[start_index:end_index]
            
            # Ensure the URL has the correct HTTPS prefix
            if not gif_url.startswith('http'):
                gif_url = 'https://' + gif_url
            
            return gif_url  # Return the direct GIF URL
    except Exception as e:
        print(f"Error fetching GIF: {e}")  # Debugging line for errors
    return None  # Return None if anything goes wrong



# Initialize database connection
conn = sqlite3.connect('blacklist.db')
c = conn.cursor()

# Create a table to store blacklisted messages if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS blacklisted_messages (
                message_id INTEGER PRIMARY KEY
            )''')
conn.commit()


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=[".", "<@1285858287404847185> ", "<@1285858287404847185>"], intents=intents)

bot.remove_command('help')
bot.remove_command('strike')

async def setstauts():
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="""The object of golf is to play the least amount of golf."""))

async def print_joke():
    j = await Jokes()  # Initialise the class
    joke = await j.get_joke(blacklist=['nsfw', 'racist', 'religious', 'political', 'sexist', 'explicit'])  # Retrieve a random joke
    if joke["type"] == "single": # Print the joke
        return joke["joke"]
    else:
        return str(f"{joke['setup']}, {joke['delivery']}")

def get_random_dad_joke():
    response = requests.get('https://icanhazdadjoke.com/', headers={'Accept': 'application/json'})
    if response.status_code == 200:
        joke = response.json()['joke']
        return joke
    else:
        return "Oops! Couldn't fetch a joke."

@bot.hybrid_command(name="addreaction", description='Add a reaction to a message')
@app_commands.describe(message_id='The message ID', reaction="Reaction to add.", channel="The channel the message is in, required if the message is in a different channel.")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def command(ctx, message_id: discord.Message, reaction: str, channel: discord.TextChannel = None):
    if channel == None:
        channel = ctx.channel
    try:
        # Fetch the message using the message_id
        message = await channel.fetch_message(int(message_id.id))

        # Add the reaction to the message
        await message.add_reaction(reaction)

        await ctx.send(f"Reaction '{reaction}' added to the message.", ephemeral=True)
    except discord.NotFound:
        await ctx.send("Message not found.", ephemeral=True)
    except discord.HTTPException:
        await ctx.send("Failed to add the reaction.", ephemeral=True)

@bot.hybrid_command(name="modnick", description='Moderate a users nickname')
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def modnick(ctx, user: discord.Member):
    adj=["mindless", "pointless", "brilliant", "mediocre", "overhyped", 
    "adequate", "lazy", "predictable", "broken", "clueless",
    "epic", "useless", "dynamic", "frustrating", "tragic",
    "vibrant", "awkward", "tedious", "chaotic", "unrealistic",
    "flawless", "dull", "unstable", "perfect", "clumsy",
    "ridiculous", "mundane", "inevitable", "absurd", "tragic",
    "majestic", "forgettable", "pretentious", "annoying", "hilarious",
    "lethargic", "stubborn", "awkward", "cryptic", "senseless",
    "awkward", "inefficient", "baffling", "timeless", "pointless",
    "ambitious", "tragic", "superficial", "satisfying", "tedious"]
    noun=["genius", "disaster", "miracle", "catastrophe", "illusion", 
    "nuisance", "failure", "victory", "nightmare", "travesty",
    "legend", "mess", "chaos", "debacle", "masterpiece", 
    "fiasco", "mystery", "paradox", "contradiction", "blunder", 
    "drama", "charade", "enigma", "glitch", "circus", 
    "meltdown", "spectacle", "puzzle", "hoax", "catastrophe", 
    "scheme", "farce", "scandal", "tragedy", "comedy", 
    "myth", "illusion", "whirlwind", "dilemma", "riddle", 
    "illusion", "mirage", "joke", "conundrum", "fantasy", 
    "labyrinth", "mirage", "quandary", "saga", "whim"]
    nickname = str(choice(adj)+choice(noun))
    if len(nickname) > 32:
        nickname = nickname[:32]
    try:
        await user.edit(nick=nickname)
        await ctx.send(f"Nickname set to: {nickname}")
    except discord.errors.Forbidden:
        await ctx.send("I can't moderate that user's nickname.")
    except discord.errors.HTTPException as e:
        await ctx.send(f"Failed to set nickname due to an error: {str(e)}")

@bot.command(name= 'Watch')
@commands.is_owner()
async def Watch(ctx):
    await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Bros"))

@bot.hybrid_command(name='membercount', aliases=['members'], description='View the servers member count')
async def membercount(ctx):
    members = ctx.author.guild.members
    bot_count = 0
    human_count = 0
    for i in members:
        member = i.bot
        if member == True:
            bot_count += 1
    human_count = ctx.guild.member_count - bot_count
    embed = discord.Embed(title="Member Count")
    embed.add_field(name="Humans", value=f"{human_count}")
    embed.add_field(name="Bots", value=f"{bot_count}")
    embed.add_field(name="Total", value=f"{ctx.guild.member_count}")
    await ctx.send(embed=embed)


def restart_bot():
  os.execv(sys.executable, ['python'] + sys.argv)

@bot.hybrid_command(name= 'ping', description= "Ping!")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! My latency is {latency} ms.', ephemeral=True)

@bot.tree.command(name="send", description="Send a message as the bot")
@app_commands.describe(text = "What do I send?", channel = "What channel do I sent the topic to?")
@app_commands.default_permissions(manage_messages=True)
async def send(interaction, text: str, channel: discord.channel.TextChannel=None):
    if channel == None:
        channel = interaction.channel
    else:
        pass
    await interaction.response.send_message(str("Sent!"), ephemeral= True)
    print(channel.id)
    await channel.send(content=text, allowed_mentions=discord.AllowedMentions.none())

@bot.hybrid_command(name= 'help', description= "Open the Help Menu")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def help(ctx):
    HelpEmbed = discord.Embed(title="Anti-Sleep Help Menu", description="Prefix: .", color=0x00ff00)
    HelpEmbed.add_field(name="topic", value="Generate a random topic\n"
                        "Optional arguments: Channel", inline=False)
    HelpEmbed.add_field(name="revive", value="Generate a topic and ping dead chat ping\n"
                        "Optional arguments: Channel", inline=False)
    HelpEmbed.add_field(name="slowmode", value="View/Set the slowmode\n"
                        "Optional arguments: Duration, Reason", inline=False)
    HelpEmbed.add_field(name="send", value="Send a message as the bot (slash command only)", inline=False)
    HelpEmbed.add_field(name="tag", value="Display a tag (slash command only)", inline=False)
    HelpEmbed.add_field(name="purge", value="Purge up to 100 messages", inline=False)
    HelpEmbed.add_field(name="clean", value="Clean up to 100 messages from a certain user", inline=False)
    HelpEmbed.add_field(name="joke", value="Get a random joke", inline=False)
    HelpEmbed.add_field(name="dadjoke", value="Get a random dad joke", inline=False)
    HelpEmbed.add_field(name="membercount", value="Display the servers member count", inline=False)
    HelpEmbed.add_field(name="addreaction", value="Add a reaction to a message\n"
    "Arguments: message, reaction, channel(if the message is in a different channel)", inline=False)
    await ctx.send(embed=HelpEmbed, ephemeral= True)

@bot.hybrid_command(name="joke", description="Get a joke.")
async def joke(interaction):
    await interaction.defer()
    await interaction.send(str(await print_joke()))

@bot.hybrid_command(name="dadjoke", description="Get a dad joke.")
async def joke(interaction):
    await interaction.defer()
    await interaction.send(str(get_random_dad_joke()))

@bot.hybrid_command(name="purge", description="Bulk delete messages")
@app_commands.describe(amount='How many messages should I delete?', reason="Why am I deleting these?")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def purge(ctx, amount: int, *, reason="No Reason Provided"):
    channel = ctx.channel
    await ctx.defer()
    messages = [message async for message in ctx.channel.history(limit=amount, before=ctx.message)]
    await channel.delete_messages(messages, reason=reason)
    await ctx.send(f'Deleted {len(messages)} messages with the reason {reason}!', allowed_mentions=discord.AllowedMentions.none())

@bot.hybrid_command(name="clean", description="Bulk delete messages from a certain user")
@app_commands.describe(amount='How many messages should I delete?', reason="Why am I deleting these?", user="Whose messages am I deleting?")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def purge(ctx, amount: int, user: discord.user.User, *, reason="No Reason Provided"):
    await ctx.defer()
    to_delete = []

    # Fetch messages
    async for message in ctx.channel.history(limit=1000):
        if message.author == user and len(to_delete) < amount:
            to_delete.append(message)  # Append the message object directly

    # Delete messages
    if to_delete:
        await ctx.channel.delete_messages(to_delete, reason=reason)
        await ctx.send(f'Deleted {len(to_delete)} messages from the user {user.name} with the reason {reason}!', allowed_mentions=discord.AllowedMentions.none())
    else:
        await ctx.send(f'No messages found from {user.name} to delete.', allowed_mentions=discord.AllowedMentions.none())

@bot.command(name= 'restart')
@commands.is_owner()
async def restart(ctx):
    id = str(ctx.author.id)
    if id == '902784993301004348':
        await ctx.send("Restarting bot...")
        print(f'Restart Executed')
        restart_bot()
        await ctx.send("Complete")
    else:
        await ctx.send("Imagine not having perms")

@bot.command(name= 'topic', description= "Generate a topic")
@commands.has_permissions(manage_messages=True)
async def topic(ctx, channel: discord.channel.TextChannel=None):
    if channel is None:
        channel = ctx.channel  # Default to the channel where the command was invoked

    try:
        response = requests.get('https://www.conversationstarters.com/random.php')
        response.raise_for_status()  # Ensure the request was successful

        soup = BeautifulSoup(response.text, 'html.parser')
        starter = soup.get_text().strip()  # Get all text, but let's make it smarter later

        if starter:
            await channel.send(f"# {starter}")
        else:
            await ctx.send("Could not find a conversation starter.")  # Send a message in the command context
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")  # Send error in the command context

@bot.tree.command(name= 'topic', description= "Generate a topic")
@app_commands.describe(channel = "What channel do I sent the topic to?")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.default_permissions(manage_messages=True)
async def topic(interaction, channel: discord.channel.TextChannel=None):
    if channel is None:
        channel = interaction.channel  # Default to the channel where the command was invoked
    await interaction.response.send_message("Sent!", ephemeral=True)
    try:
        response = requests.get('https://www.conversationstarters.com/random.php')
        response.raise_for_status()  # Ensure the request was successful

        soup = BeautifulSoup(response.text, 'html.parser')
        starter = soup.get_text().strip()  # Get all text, but let's make it smarter later

        if starter:
            await channel.send(f"# {starter}")
        else:
            await interaction.followup.send("Could not find a conversation starter.")  # Send a message in the command context
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")  # Send error in the command context

@bot.command(name='revive', description="Generate a topic and ping dead chat")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def revive(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel  # Default to the channel where the command was invoked
    if channel.guild.id == 1081122313870778471:
        try:
            response = requests.get('https://www.conversationstarters.com/random.php')
            response.raise_for_status()  # Ensure the request was successful

            soup = BeautifulSoup(response.text, 'html.parser')
            starter = soup.get_text().strip()  # Get all text, but let's make it smarter later

            if starter:
                await channel.send(f"# <@&1224606858367471667> {starter}")
            else:
                await ctx.send("Could not find a conversation starter.")  # Send a message in the command context
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")  # Send error in the command context
    else:
        await ctx.send("This command is not compatible with this guild!")


@bot.tree.command(name= 'revive', description= "Generate a topic and ping dead chat ping")
@app_commands.describe(channel = "What channel do I sent the topic to?")
@app_commands.default_permissions(manage_messages=True)
async def revive(interaction, channel: discord.channel.TextChannel=None):
    if channel is None:
        channel = interaction.channel  # Default to the channel where the command was invoked
    if channel.guild.id == 1081122313870778471:
        try:
            await interaction.response.send_message("Sent!", ephemeral=True)
            response = requests.get('https://www.conversationstarters.com/random.php')
            response.raise_for_status()  # Ensure the request was successful

            soup = BeautifulSoup(response.text, 'html.parser')
            starter = soup.get_text().strip()  # Get all text, but let's make it smarter later

            if starter:
                await channel.send(f"# <@&1224606858367471667> {starter}")
            else:
                await interaction.followup.send("Could not find a conversation starter.")  # Send a message in the command context
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")  # Send error in the command context
    else:
        await interaction.response.send_message("This command is not compatible with this guild!", ephemeral=True)

@bot.hybrid_command(name= 'slowmode', description= "View/Set the slowmode", aliases=["sm", "setslowmode"])
@app_commands.describe(reason='Why are you setting the slowmode?', duration = "What are you setting the slowmode to? Type 0s to disable.")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def slowmode(ctx, duration:str = "Hi,IAmDefaultValue", *, reason: str = commands.parameter(default="No Reason Provided", description="Seconds to set the slowmode too, set to 0 to disable.")):
    duration_send = None
    if duration != "Hi,IAmDefaultValue":
        duration_send = timeparse(duration)
    else:
        time = datetime.timedelta(seconds=ctx.channel.slowmode_delay)
        await ctx.send(f"Slowmode is currently set to {time}")
        return
    if duration_send == None and duration != "Hi,IAmDefaultValue":
        await ctx.send("Please provide a vaild duration (for example: 30m)")
    else:
        if duration_send!="Hi,IAmDefaultValue" and duration_send < 21600 or duration_send == 21600:
            await ctx.channel.edit(slowmode_delay=duration_send, reason=reason)
            await ctx.send("Slowmode set to "+duration+" with the reason "+reason+"!", allowed_mentions=discord.AllowedMentions.none())
        elif duration_send > 21600 and duration_send!="Hi,IAmDefaultValue":
            await ctx.send("Slowmode cannot exceed 6 hours.")

@bot.command(name= 'sync')
@commands.is_owner()
async def sync(ctx):
    print("sync command")
    if str(ctx.author.id) == "902784993301004348":
        await bot.tree.sync()
        await ctx.send('Command tree synced.')
    else:
        await ctx.send('You must be the owner to use this command!')

@bot.command(name= 'shutdown')
@commands.is_owner()
async def shutdown(ctx):
    print("shutdown command")
    if str(ctx.author.id) == "902784993301004348":
        await ctx.send('Shutting down...')
        await ctx.bot.close()
        quit()
    else:
        await ctx.send('You must be the owner to use this command!')

@bot.tree.command(name= "tags", description="Send a tag")
@app_commands.describe(tag='Tags to choose from')
@app_commands.default_permissions(manage_messages = True)
@app_commands.choices(
    tag=[
    app_commands.Choice(name='Anti-Sleep Invite', value="Anti-Sleep Invite"),
    app_commands.Choice(name='Media', value="Media"),
    app_commands.Choice(name='Anti-Sleep', value="Anti-Sleep"),
    app_commands.Choice(name='Applications', value="Applications"),
    app_commands.Choice(name='Quotes', value="Quotes"),
    app_commands.Choice(name='Hosting', value="Hosting")
])
async def tag(interaction, tag: app_commands.Choice[str]):
    tag = tag.name
    if interaction.guild.id == 1081122313870778471:
        if tag == "media" or tag == "Media":
            await interaction.response.send_message("Sent!", ephemeral= True)
            channel = interaction.channel
            MediaTagEmbed = discord.Embed(title="Tag - Media", description="**Why can't I send media?**\n"
                                        "At Level Five you unlock media in <#1232086351093039164> and <#1161884115885379625>\n"
                                        "At Level Twenty-Five you unlock media everywhere else!", color=0x00ff00)
            await channel.send(embed=MediaTagEmbed)
        elif tag == "anti-sleep invite" or tag == "Anti-Sleep Invite":
            await interaction.response.send_message("Sent!", ephemeral= True)
            channel = interaction.channel
            AntiSleepTagEmbed = discord.Embed(title="Tag - Anti-Sleep Invite", description="**Why can't I invite Anti-Sleep?**\n"
                                        "Anti-Sleep is a Private Bot made by <@902784993301004348> for this server, it is not publically available.", color=0x00ff00)
            await channel.send(embed=AntiSleepTagEmbed)
        elif tag == "anti-sleep" or tag == "Anti-Sleep":
            await interaction.response.send_message("Sent!", ephemeral= True)
            channel = interaction.channel
            AntiSleepTagEmbed = discord.Embed(title="Tag - Anti-Sleep ", description="**What is Anti-Sleep?**\n"
                                        "Anti-Sleep is a Private Bot made by <@902784993301004348> for this server.\n" 
                                        "it is being updated every day with the goal of one day keeping chat alive.\n" 
                                        "It's commands require the Manage Messages permission to use because it is a bot designed only to be used by Staff.\n"
                                        "As it is a Private Bot, it is not publically available.", color=0x00ff00)
            await channel.send(embed=AntiSleepTagEmbed)
        elif tag == "applications" or tag == "Applications":
            await interaction.response.send_message("Sent!", ephemeral= True)
            channel = interaction.channel
            ApplicationTagEmbed = discord.Embed(title="Tag - Applications ", description="**How do I apply?**\n"
                                        "Moderator applications are currently **__closed__**, News Ping will be pinged when they open.\n"
                                        "Event planner applications are currently **__open__**, Head to https://discord.com/channels/1081122313870778471/1224550149548671168 to apply.", color=0x00ff00)
            await channel.send(embed=ApplicationTagEmbed)
        elif tag == "quotes" or tag == "Quotes":
            await interaction.response.send_message("Sent!", ephemeral= True)
            channel = interaction.channel
            QuoteTagEmbed = discord.Embed(title="Tag - Make It A Quote", description="**What is Make it a quote?**\n"
                                        "Make it a quote is a bot that makes quotes of messages. It is added for humorous perpouses.\n"
                                        "Do not spam it, you will be warned.\n"
                                        "How do I get started? Gald you asked. Reply to a message and in the reply ping the bot and it'll make a quote for you.\n"
                                        "You can also add extra tags to make the quote look different! They are\n"
                                        "light (l) : Makes the background of the image white, color (c) : Color the user icon, flip (f) : Flip the image, bold (b) : Make the text bold, new (n) : Use new type image generation, font=<Font name> : Change the font to the specified one.", color=0x00ff00)
            await channel.send(embed=QuoteTagEmbed)
        elif tag == "hosting" or tag == "Hosting":
            await interaction.response.send_message("Sent!", ephemeral= True)
            channel = interaction.channel
            TagListEmbed = discord.Embed(title="Tag - Hosting", description="**How is Anti-Sleep hosted?**\n"
                                        "Anti-Sleep is currently hosted at a Vultr data center in New Jersey.\n"
                                        "You guys happy now?", color=0x00ff00)
            await channel.send(embed=TagListEmbed)
    else:
        await interaction.response.send_message("This command is not compatible with this guild!", ephemeral=True)

# Function to check if a message is blacklisted
def is_message_blacklisted(message_id):
    c.execute("SELECT message_id FROM blacklisted_messages WHERE message_id=?", (message_id,))
    return c.fetchone() is not None

# Function to add a message to the blacklist
def blacklist_message(message_id):
    c.execute("INSERT INTO blacklisted_messages (message_id) VALUES (?)", (message_id,))
    conn.commit()

# Your bot event code
@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id == 1081122313870778471:
        channel = payload.channel_id
        channel_obj = await bot.fetch_channel(channel)
        send_channel_sob = bot.get_channel(1287919598380912670)
        send_channel_skull = bot.get_channel(1235495254170271784)
        message_id = payload.message_id
        
        # Check if the message is blacklisted using the database
        if is_message_blacklisted(message_id):
            return  # If the message is blacklisted, skip the rest
        
        # Fetch the message
        message = await channel_obj.fetch_message(message_id)
        
        for reaction in message.reactions:
            if reaction.count == 3:  # Check the reaction count first
                if reaction.emoji == "😭" and channel != 1287919598380912670 and message.guild.id == 1081122313870778471 and channel != 1235495254170271784:
                    # Blacklist the message in the database
                    blacklist_message(message_id)
                    
                    # Create and send the embed based on message content
                    embed = discord.Embed(title="😭", description=f"{message.content}")
                    if message.attachments:
                        embed.set_image(url=message.attachments[0].url)
                    elif message.embeds:
                        if 'tenor.com' in message.embeds[0].url in message.embeds[0].url:
                            url = get_direct_gif_url(message.embeds[0].url)
                            print(url)
                            embed.set_image(url=url)
                        else:
                            embed.set_image(url=message.embeds[0].url)
                    elif message.stickers:
                        embed.set_image(url=message.stickers[0].url)
                    embed.add_field(name="Author", value=f"<@{message.author.id}>")
                    embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                    
                    # Send the embed to the designated channel
                    sent_message = await send_channel_sob.send(embed=embed)
                    await sent_message.add_reaction("😭")  # React to the message

                elif reaction.emoji == "💀" and channel != 1235495254170271784 and message.guild.id == 1081122313870778471 and channel != 1287919598380912670:
                    # Blacklist the message in the database
                    blacklist_message(message_id)
                    
                    # Create and send the embed based on message content
                    embed = discord.Embed(title="💀", description=f"{message.content}")
                    if message.attachments:
                        embed.set_image(url=message.attachments[0].url)
                    elif message.embeds:
                        if 'tenor.com' in message.embeds[0].url in message.embeds[0].url:
                            url = get_direct_gif_url(message.embeds[0].url)
                            print(url)
                            embed.set_image(url=url)
                        else:
                            embed.set_image(url=message.embeds[0].url)
                    elif message.stickers:
                        embed.set_image(url=message.stickers[0].url)
                    embed.add_field(name="Author", value=f"<@{message.author.id}>")
                    embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                    
                    # Send the embed to the designated channel
                    sent_message = await send_channel_skull.send(embed=embed)
                    await sent_message.add_reaction("💀")  # React to the message
                elif reaction.emoji.id == 1295623161311658086 and channel != 1235495254170271784 and message.guild.id == 1081122313870778471 and channel != 1287919598380912670:
                        # Blacklist the message in the database
                        blacklist_message(message_id)
                        
                        # Create and send the embed based on message content
                        embed = discord.Embed(title="💀", description=f"{message.content}")
                        if message.attachments:
                            embed.set_image(url=message.attachments[0].url)
                        elif message.embeds:
                            if 'tenor.com' in message.embeds[0].url in message.embeds[0].url:
                                url = get_direct_gif_url(message.embeds[0].url)
                                print(url)
                                embed.set_image(url=url)
                            else:
                                embed.set_image(url=message.embeds[0].url)
                        elif message.stickers:
                            embed.set_image(url=message.stickers[0].url)
                        embed.add_field(name="Author", value=f"<@{message.author.id}>")
                        embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                        
                        # Send the embed to the designated channel
                        sent_message = await send_channel_skull.send(embed=embed)
                        await sent_message.add_reaction("💀")  # React to the message
                        
                        embed = discord.Embed(title="😭", description=f"{message.content}")
                        if message.attachments:
                            embed.set_image(url=message.attachments[0].url)
                        elif message.embeds:
                            if 'tenor.com' in message.embeds[0].url in message.embeds[0].url:
                                url = get_direct_gif_url(message.embeds[0].url)
                                print(url)
                                embed.set_image(url=url)
                            else:
                                embed.set_image(url=message.embeds[0].url)
                        elif message.stickers:
                            embed.set_image(url=message.stickers[0].url)
                        embed.add_field(name="Author", value=f"<@{message.author.id}>")
                        embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                        
                        # Send the embed to the designated channel
                        sent_message = await send_channel_sob.send(embed=embed)
                        await sent_message.add_reaction("😭")  # React to the message
                else:
                    print("No relevant reaction.")


    if payload.guild_id == 1268137172288929906:
        channel = payload.channel_id
        channel_obj = await bot.fetch_channel(channel)
        send_channel_skull = bot.get_channel(1291183423720919181)
        message_id = payload.message_id
        message = await discord.TextChannel.fetch_message(channel_obj, message_id) 
        for reaction in message.reactions:
            if reaction.emoji == "💀":
                if reaction.count == 3 and channel != 1291183423720919181 and message.guild.id == 1268137172288929906:
                    if message.attachments:
                        embed = discord.Embed(title="💀", description=f"{message.content}")
                        embed.set_image(url=message.attachments[0].url)
                        embed.add_field(name="Author", value=f"<@{message.author.id}>")
                        embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                    elif message.embeds:
                        embed = discord.Embed(title="💀", description=f"{message.content}")
                        embed.set_image(url=message.embeds[0].url)
                        embed.add_field(name="Author", value=f"<@{message.author.id}>")
                        embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                    elif not message.attachments and not message.embeds:
                        embed = discord.Embed(title="💀", description=f"{message.content}")
                        embed.add_field(name="Author", value=f"<@{message.author.id}>")
                        embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                    await send_channel_skull.send(embed=embed)
                    await send_channel_skull.last_message.add_reaction("💀")
'''
@bot.tree.command(name="strike", description="Add a strike to a staff member")
@app_commands.checks.has_role(1133294652439679006)
@app_commands.describe(staff="Who do I strike?", reason="Why am I striking them?")
async def strike(interaction, staff: discord.member.Member, reason: str):
    await interaction.response.defer()
    await interaction.followup.send(f"Gave {staff} a strike for {reason}.")
'''
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.NotOwner):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I do not have permissions to run this command, Please ping Crazy_Dog.py!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, discord.Forbidden):
        await ctx.send("I do not have permissions to do that! Please ping Crazy_Dog.py!")
    elif isinstance (error, commands.errors.MissingRequiredArgument):
        missing_arg = error.param.name
        await ctx.send(f"You are missing a required argument ({missing_arg})!")
    elif isinstance (error, commands.errors.BadArgument):
        await ctx.send("You did not input an argument correctly!")
    elif isinstance (error, commands.CommandNotFound):
        return
    else:
        await ctx.send(f"An unexpected error occurred. `{error}`")
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    logging.exception('Ignoring exception in command "%s"', str(ctx.command), exc_info=error)

@bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingRole):
        if interaction.response.is_done():
            await interaction.followup.send(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
        else:
            await interaction.response.send_message(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
    elif isinstance(error, app_commands.MissingRole):
        if interaction.response.is_done():
            await interaction.followup.send(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
        else:
            await interaction.response.send_message(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
    elif isinstance(error, discord.Forbidden):
        if interaction.response.is_done():
            await interaction.followup.send("I do not have permissions to do that! Please ping Crazy_Dog.py!")
        else:
            await interaction.response.send_message("I do not have permissions to do that! Please ping Crazy_Dog.py!")
    elif isinstance(error, app_commands.MissingAnyRole):
        if interaction.response.is_done():
            await interaction.followup.send(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
        else:
            await interaction.response.send_message(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        if interaction.response.is_done():
            await interaction.followup.send("I do not have permissions to run this command, Please ping Crazy_Dog.wbfs!", ephemeral= True)
        else:
            await interaction.response.send_message("I do not have permissions to run this command, Please ping Crazy_Dog.wbfs!", ephemeral= True)
    elif isinstance(error, app_commands.MissingPermissions):
        if interaction.response.is_done():
            await interaction.followup.send(f"You do not have permissions to run this command ({interaction.command.name})!",ephemeral= True)
        else:
            await interaction.response.send_message(f"You do not have permissions to run this command ({interaction.command.name})!", ephemeral= True)
    else:
        if interaction.response.is_done():
            await interaction.followup.send(f"An unexpected error occurred. `{error}`", ephemeral= True)
        else:
            await interaction.response.send_message(f"An unexpected error occurred. `{error}`", ephemeral= True)
    print('Ignoring exception in command {}:'.format(interaction.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    logging.exception('Ignoring exception in command "%s"', str(interaction.command), exc_info=error)

@bot.event
async def on_message(message):
    content = str.lower(message.content)
    if "<@773514543468642314>" in content or "chatgpt" in content or "gpt" in content:
        await message.add_reaction("<:GunL:1287914114949316628>")
        await message.add_reaction("<:ChatGPT:1296703572120961125>")
        await message.add_reaction("<:GunR:1287637527129493580>")
    if "<@880339013012193331>" in content or "woah" in content or "woahgamer" in content:
        await message.add_reaction("🎮")
    if "<@902784993301004348>" in content or "crazy" in content or "dog" in content or "crazydog" in content:
        await message.add_reaction("<:GunL:1287914114949316628>")
        await message.add_reaction("<:duoSuper:1298919437931384842>")
        await message.add_reaction("<:GunR:1287637527129493580>")
    if "<@1287634742321221676>" in content or "duo" in content:
        await message.add_reaction("<:GunL:1287914114949316628>")
        await message.add_reaction("<:Duo:1287637513749397565>")
        await message.add_reaction("<:GunR:1287637527129493580>")
    if "meek" in content or "meekzombii" in content or "<@903440182278258708>" in content:
        await message.add_reaction("<a:dancingalien:1289366751213129750>")
    await bot.process_commands(message)

class ApplicationView(ui.View):
    def __init__(self, user, timeout=9999999999):  # Default timeout is 600 seconds (10 minutes)
        super().__init__(timeout=timeout)
        self.user = user
        self.message = None

    @ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        # Action when the "Approve" button is clicked
        await interaction.response.send_message(f"{self.user.mention} has been approved as a moderator!", ephemeral=False)
        await self.user.send("You have been approved for moderator!")
        guild = bot.get_guild(1081122313870778471)
        tmod = guild.get_role(1224549822162403360)
        await guild.get_member(self.user.id).add_roles(tmod)
        # Perform any additional actions here, e.g., assigning roles
        self.stop()

    @ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        # Action when the "Deny" button is clicked
        await interaction.response.send_message(f"{self.user.mention}'s application has been denied.", ephemeral=False)
        await self.user.send("You have been denied for moderator!")
        # Perform any additional actions here, e.g., sending a denial message
        self.stop()
    
    async def on_timeout(self):
        # Disable buttons after timeout
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(content="This application has timed out.", view=self)
        print("View timed out")  # Debugging message

class ApplicationViewEvent(ui.View):
    def __init__(self, user, timeout=9999999999):  # Default timeout is 600 seconds (10 minutes)
        super().__init__(timeout=timeout)
        self.user = user
        self.message = None

    @ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        # Action when the "Approve" button is clicked
        await interaction.response.send_message(f"{self.user.mention} has been approved as an event planner!", ephemeral=False)
        await self.user.send("You have been approved for event planner!")
        guild = bot.get_guild(1081122313870778471)
        ep = guild.get_role(1246699624773845004)
        await guild.get_member(self.user.id).add_roles(ep)
        # Perform any additional actions here, e.g., assigning roles
        self.stop()

    @ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        # Action when the "Deny" button is clicked
        await interaction.response.send_message(f"{self.user.mention}'s application has been denied.", ephemeral=False)
        await self.user.send("You have been denied for event planner!")
        # Perform any additional actions here, e.g., sending a denial message
        self.stop()
    
    async def on_timeout(self):
        # Disable buttons after timeout
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(content="This application has timed out.", view=self)
        print("View timed out")  # Debugging message
    

class ModApplicationSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderator Application", emoji="🔨", description="Apply for mod!", value="mod"),
            discord.SelectOption(label="Event Planner", emoji="📆", description="Apply for event planner!", value="event"),
        ]
        # Initialize the parent Select class with the options
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    # Define the callback function for when an option is selected
    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        if value == "mod":
            guild = bot.get_guild(1081122313870778471)
            user = interaction.user
            for role in guild.get_member(user.id).roles:
                if role.id == 1224662390453436547:
                    await interaction.response.send_message("You are already a staff member")
                    return
            in_app.append(user.id)
            await interaction.response.send_message(content="Starting application process, if you want to cancel at anytime say `.cancel`")
            await user.send(content="How old are you?")
            Age = await bot.wait_for('message', check=lambda m: m.author == user)
            if Age.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send(content="Why do you want to be mod?")
            Why = await bot.wait_for('message', check=lambda m: m.author == user)
            if Why.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send(content="What timezone are you in?")
            time = await bot.wait_for('message', check=lambda m: m.author == user)
            if time.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send("Thank you for your application! Here are your responses:")
            await user.send(f"Age:{Age.content}")
            await user.send(f"Why you want mod:{Why.content}")
            await user.send(f"Your Timezone:{time.content}")
            in_app.remove(user.id)
            channel = bot.get_channel(1224550220721815564)
            view2=ApplicationView(user)
            await channel.send(f"{user.mention}'s application for moderator.\n"
                            f"Age:{Age.content}\n"
                            f"Why they want mod:{Why.content}\n"
                            f"Their Timezone:{time.content}", view=view2)
        if value == "event":
            guild = bot.get_guild(1081122313870778471)
            user = interaction.user
            for role in guild.get_member(user.id).roles:
                if role.id == 1224662390453436547:
                    await interaction.response.send_message("You are already an event planner")
                    return
                if role.id == 1246699624773845004:
                    await interaction.response.send_message("You are already an event planner")
                    return
            in_app.append(user.id)
            await interaction.response.send_message(content="Starting application process, if you want to cancel at anytime say `.cancel`")
            await user.send(content="How old are you?")
            Age = await bot.wait_for('message', check=lambda m: m.author == user)
            if Age.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send(content="Why do you want to be an event planner?")
            Why = await bot.wait_for('message', check=lambda m: m.author == user)
            if Why.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send(content="What ideas do you have for events?")
            what = await bot.wait_for('message', check=lambda m: m.author == user)
            if what.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send(content="What timezone are you in?")
            time = await bot.wait_for('message', check=lambda m: m.author == user)
            if time.content.lower() == '.cancel':
                await user.send("Application process has been cancelled.")
                in_app.remove(user.id)
                return  # Exit the function early
            await user.send("Thank you for your application! Here are your responses:")
            await user.send(f"Age:{Age.content}")
            await user.send(f"Why you want this job:{Why.content}")
            await user.send(f"What ideas do you have for events:{what.content}")
            await user.send(f"Your Timezone:{time.content}")
            in_app.remove(user.id)
            channel = bot.get_channel(1224550220721815564)
            view2=ApplicationViewEvent(user)
            await channel.send(f"{user.mention}'s application for event planner.\n"
                            f"Age:{Age.content}\n"
                            f"Why they want this job:{Why.content}\n"
                            f"What ideas do they have for events:{what.content}\n"
                            f"Their Timezone:{time.content}", view=view2)

# Create a View that holds the Select menu
class SelectView(discord.ui.View):
    def __init__(self, *, timeout=9999999999):
        super().__init__(timeout=timeout)
        self.add_item(ModApplicationSelect())  # Add the select menu to the view


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id in in_app:
            pass
        elif message.author.id == 1285858287404847185:
            return
        else:
            if message.author in bot.get_guild(1081122313870778471).members:
                await message.reply(content="Select a form to fill out.", view=SelectView())
            else:
                await message.reply(content="Something coming soon.")
    await bot.process_commands(message)

@bot.event
async def on_ready():
    await setstauts()
    print(f'We have logged in as {bot.user}')


discord.utils.setup_logging(handler=handler)
bot.run("MTI4NTg1ODI4NzQwNDg0NzE4NQ.G4yG2-.i0OHXN-hrX8RszKAk1Vo437BnE9BW6hvONzn5Y", log_handler=handler)     