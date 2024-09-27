import discord 
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from pytimeparse.timeparse import timeparse
import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

bot.remove_command('help')

async def setstauts():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Bros"))

@bot.command(name= 'Watch')
@commands.is_owner()
async def Watch(ctx):
    await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Bros"))

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
async def send(interaction, text: str, channel: discord.channel.TextChannel):
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
    await ctx.send(embed=HelpEmbed, ephemeral= True)

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
async def purge(ctx, amount: int, user: discord.Member, *, reason="No Reason Provided"):
    await ctx.defer()
    to_delete = []

    # Fetch messages
    async for message in ctx.channel.history(limit=1000):
        if message.author == user and len(to_delete) < amount:
            to_delete.append(message)  # Append the message object directly

    # Delete messages
    if to_delete:
        await ctx.channel.delete_messages(to_delete)
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
            await interaction.send("Could not find a conversation starter.")  # Send a message in the command context
    except Exception as e:
        await interaction.send(f"An error occurred: {str(e)}")  # Send error in the command context

@bot.command(name='revive', description="Generate a topic and ping dead chat")
@commands.has_permissions(manage_messages=True)
@app_commands.default_permissions(manage_messages=True)
async def revive(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel  # Default to the channel where the command was invoked

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


@bot.tree.command(name= 'revive', description= "Generate a topic and ping dead chat ping")
@app_commands.describe(channel = "What channel do I sent the topic to?")
@app_commands.default_permissions(manage_messages=True)
async def revive(interaction, channel: discord.channel.TextChannel=None):
    if channel is None:
        channel = interaction.channel  # Default to the channel where the command was invoked
    await interaction.response.send_message("Sent!", ephemeral=True)
    try:
        response = requests.get('https://www.conversationstarters.com/random.php')
        response.raise_for_status()  # Ensure the request was successful

        soup = BeautifulSoup(response.text, 'html.parser')
        starter = soup.get_text().strip()  # Get all text, but let's make it smarter later

        if starter:
            await channel.send(f"# <@&1224606858367471667> {starter}")
        else:
            await interaction.send("Could not find a conversation starter.")  # Send a message in the command context
    except Exception as e:
        await interaction.send(f"An error occurred: {str(e)}")  # Send error in the command context

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
    app_commands.Choice(name='List', value="List"),
    app_commands.Choice(name='Anti-Sleep Invite', value="Anti-Sleep Invite"),
    app_commands.Choice(name='Media', value="Media"),
    app_commands.Choice(name='Anti-Sleep', value="Anti-Sleep"),
    app_commands.Choice(name='Applications', value="Applications"),
    app_commands.Choice(name='Quotes', value="Quotes")
])
async def tag(interaction, tag: app_commands.Choice[str]):
    tag = tag.name
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
                                      "Moderator applications are currently **__open__**, to apply head to https://discord.com/channels/1081122313870778471/1224550149548671168.\n"
                                      "Event planner applications are currently **__closed__**, News Ping will be pinged when they open.", color=0x00ff00)
        await channel.send(embed=ApplicationTagEmbed)
    elif tag == "quotes" or tag == "Quotes":
        await interaction.response.send_message("Sent!", ephemeral= True)
        channel = interaction.channel
        QuoteTagEmbed = discord.Embed(title="Tag - Make It A Quote", description="**What is Make it a quote?**\n"
                                      "Make it a quote is a bot that makes quotes of messages. It is added for humorous perpouses.\n"
                                      "Do not spam it, you will be warned.\n"
                                      "How do I get started? Gald you asked. Reply to a message pinging the bot and it'll make a quote for you.", color=0x00ff00)
        await channel.send(embed=QuoteTagEmbed)
    elif tag == "list" or tag == "List":
        TagListEmbed = discord.Embed(title="Tag List", description="Media - List Media Perms Info.\n"
                                     "Anti-Sleep Invite - How do I invite this bot?\n"
                                     "Anti-Sleep - What is this bot?\n"
                                     "Applications - How do I apply?\n"
                                     "Make it a quote - What is it?", color=0x00ff00)
        await interaction.response.send_message(embed=TagListEmbed, ephemeral= True)

@bot.event
async def on_raw_reaction_add(payload):
    channel = payload.channel_id
    channel_obj = await bot.fetch_channel(channel)
    send_channel_sob = bot.get_channel(1287919598380912670)
    send_channel_skull = bot.get_channel(1235495254170271784)
    message_id = payload.message_id
    message = await discord.TextChannel.fetch_message(channel_obj, message_id) 
    for reaction in message.reactions:
        if reaction.emoji == "😭":
            if reaction.count == 3 and channel != 1287919598380912670 and message.guild.id == 1081122313870778471 and channel != 1235495254170271784:
                if message.attachments:
                    embed = discord.Embed(title="😭", description=f"{message.content}")
                    embed.set_image(url=message.attachments[0].url)
                    embed.add_field(name="Author", value=f"<@{message.author.id}>")
                    embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                elif message.embeds:
                    embed = discord.Embed(title="😭", description=f"{message.content}")
                    embed.set_image(url=message.embeds[0].url)
                    embed.add_field(name="Author", value=f"<@{message.author.id}>")
                    embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                elif not message.attachments and not message.embeds:
                    embed = discord.Embed(title="😭", description=f"{message.content}")
                    embed.add_field(name="Author", value=f"<@{message.author.id}>")
                    embed.add_field(name="Jump to message", value=f"[Click Here]({message.jump_url})")
                await send_channel_sob.send(embed=embed)
                await send_channel_sob.last_message.add_reaction("😭")
        elif reaction.emoji == "💀":
            if reaction.count == 3 and channel != 1235495254170271784 and message.guild.id == 1081122313870778471 and channel != 1287919598380912670:
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

@bot.tree.command(name="strike", description="Add a strike to a staff member")
@app_commands.checks.has_role(1133294652439679006)
@app_commands.describe(staff="Who do I strike?", reason="Why am I striking them?")
async def strike(interaction, staff: discord.member.Member, reason: str):
    await interaction.response.defer()
    await interaction.followup.send(f"Gave {staff} a strike for {reason}.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.NotOwner):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I do not have permissions to run this command, Please ping Crazy_Dog.wbfs!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send(f"You do not have permissions to run this command ({ctx.command.name})!", ephemeral= True)
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance (error, commands.errors.MissingRequiredArgument):
        missing_arg = error.param.name
        await ctx.send(f"You are missing a required argument ({missing_arg})!")
    elif isinstance (error, commands.errors.BadArgument):
        await ctx.send("You did not input an argument correctly!")
    else:
        await ctx.send(f"An unexpected error occurred. `{error}`")

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
    elif isinstance(error, app_commands.errors.CommandNotFound):
        if interaction.response.is_done():
            await interaction.followup.send("Command not found!", ephemeral= True)
        else:
            await interaction.response.send_message("Command not found!", ephemeral= True)
    else:
        if interaction.response.is_done():
            await interaction.followup.send(f"An unexpected error occurred. `{error}`", ephemeral= True)
        else:
            await interaction.response.send_message(f"An unexpected error occurred. `{error}`", ephemeral= True)

@bot.event
async def on_message(message):
    content = str.lower(message.content)
    if "<@773514543468642314>" in content or "duo" in content or "duoling" in content:
        await message.add_reaction("<:GunL:1287914114949316628>")
        await message.add_reaction("<:Duo:1287637513749397565>")
        await message.add_reaction("<:GunR:1287637527129493580>")
        await bot.process_commands(message)
    elif "<@880339013012193331>" in content or "woah" in content or "woahgamer" in content:
        await message.add_reaction("🎮")
        await bot.process_commands(message)
    elif "<@902784993301004348>" in content or "crazy" in content or "dog" in content or "crazydog" in content:
        await message.add_reaction("<:CrazyDog:1287924115344457730>")
        await message.add_reaction("<:DiscordPy:1288623578400690208>")
        await message.add_reaction("😭")
        await bot.process_commands(message)
    elif "<@1287634742321221676>" in content or "duogpt" in content or "gpt" in content:
        await message.add_reaction("<:GunL:1287914114949316628>")
        await message.add_reaction("<:Duo:1287637513749397565>")
        await message.add_reaction("<:GunR:1287637527129493580>")
        await bot.process_commands(message)
    else:
        await bot.process_commands(message)

@bot.event
async def on_ready():
    await setstauts()
    print(f'We have logged in as {bot.user}')

bot.run("MTI4NTg1ODI4NzQwNDg0NzE4NQ.G4yG2-.i0OHXN-hrX8RszKAk1Vo437BnE9BW6hvONzn5Y")