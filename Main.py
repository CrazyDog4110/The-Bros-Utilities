import discord 
import requests
from discord.ext import commands
from discord import app_commands
import os
import sys
from pytimeparse.timeparse import timeparse
from jokeapi import Jokes
import logging
import traceback
import sqlite3
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
SOBBOARD = os.getenv("SOB_BOARD")
SKULLBOARD = os.getenv("SKULL_BOARD")
MAINSERVER = os.getenv("SERVER_ID")
PREFIX = os.getenv("PREFIX")

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

bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)

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

@bot.command(name= 'Watch')
@commands.is_owner()
async def Watch(ctx):
    await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=ctx.guild.name))

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

@bot.hybrid_command(name= 'help', description= "Open the Help Menu")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def help(ctx):
    HelpEmbed = discord.Embed(title=f"{bot.user} Help Menu", description=f"Prefix: {PREFIX}", color=0x00ff00)
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

@bot.command(name= 'restart')
@commands.is_owner()
async def restart(ctx):
    id = int(ctx.author.id)
    if id == bot.owner_id:
        await ctx.send("Restarting bot...")
        print(f'Restart Executed')
        restart_bot()
        await ctx.send("Complete")
    else:
        await ctx.send("You must be bot owner to run this command.")
        
@bot.command(name= 'sync')
@commands.is_owner()
async def sync(ctx):
    print("sync command")
    if int(ctx.author.id) == bot.owner_id:
        await bot.tree.sync()
        await ctx.send('Command tree synced.')
    else:
        await ctx.send('You must be the owner to use this command!')

@bot.command(name= 'shutdown')
@commands.is_owner()
async def shutdown(ctx):
    print("shutdown command")
    if str(ctx.author.id) == bot.owner_id:
        await ctx.send('Shutting down...')
        await ctx.bot.close()
        quit()
    else:
        await ctx.send('You must be the owner to use this command!')

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
    if payload.guild_id == MAINSERVER:
        channel = payload.channel_id
        channel_obj = await bot.fetch_channel(channel)
        send_channel_sob = bot.get_channel(SOBBOARD)
        send_channel_skull = bot.get_channel(SKULLBOARD)
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

    if payload.guild_id == MAINSERVER:
        channel = payload.channel_id
        channel_obj = await bot.fetch_channel(channel)
        send_channel_skull = bot.get_channel(SKULLBOARD)
        message_id = payload.message_id
        message = await discord.TextChannel.fetch_message(channel_obj, message_id) 
        for reaction in message.reactions:
            if reaction.emoji == "💀":
                if reaction.count == 3 and channel != SKULLBOARD and message.guild.id == MAINSERVER:
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
async def on_ready():
    await bot.load_extension('cogs.topic')
    await bot.load_extension('cogs.revive')
    await bot.load_extension('cogs.utility')
    await bot.load_extension('cogs.Applications')
    await bot.load_extension('cogs.listener')
    await bot.load_extension('cogs.mediaonly')
    bot.owner_id = (await bot.application_info()).owner.id
    await setstauts()
    print(f'We have logged in as {bot.user}')

discord.utils.setup_logging(handler=handler)
bot.run(TOKEN, log_handler=handler)     
