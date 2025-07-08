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

from discord.ext import commands

class utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="send", description="Send a message as the bot")
    @app_commands.default_permissions(manage_messages=True)
    async def send(self, interaction, text: str, channel: discord.channel.TextChannel=None):
        """
        Parameters
        -----------
        text: str
            What do I send?
        channel: discord.channel.TextChannel
            What channel do I send to?
        """
        if channel == None:
            channel = interaction.channel
        else:
            pass
        await interaction.response.send_message(str("Sent!"), ephemeral= True)
        await self.bot.get_guild(1081122313870778471).get_channel(1342369080224780312).send(f'{interaction.user} said {text}')
        print(channel.id)
        await channel.send(content=text, allowed_mentions=discord.AllowedMentions.none())

    @commands.hybrid_command(name="addreaction", description='Add a reaction to a message')
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def command(self, ctx, message_id: discord.Message, reaction: str, channel: discord.TextChannel = None):
        """
        Parameters
        -----------
        message_id: discord.Message
            The message ID or URL.
        reaction: str
            Reaction to add.
        channel: discord.TextChannel
            The channel the message is in, required if the message is in a different channel.
        """
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

    @commands.hybrid_command(name= 'slowmode', description= "View/Set the slowmode", aliases=["sm", "setslowmode"])
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def slowmode(self, ctx, duration:str = "Hi,IAmDefaultValue", *, reason: str = commands.parameter(default="No Reason Provided", description="Seconds to set the slowmode too, set to 0 to disable.")):
        """
        Parameters
        -----------
        reason: str
            Why are you setting the slowmode?
        duration: str
            What are you setting the slowmode to? Type 0s to disable.
        """
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

    @commands.hybrid_command(name="clean", description="Bulk delete messages from a certain user")
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def clean(self, ctx, amount: int, user: discord.user.User, *, reason="No Reason Provided"):
        """
        Parameters
        -----------
        amount: int
            How many messages should I delete?
        user: discord.user.User
            Whose messages am I deleting?
        reason: str
            Why am I deleting these?
        """
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

    @commands.hybrid_command(name="purge", description="Bulk delete messages")
    @app_commands.describe(amount='How many messages should I delete?', reason="Why am I deleting these?")
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int, *, reason="No Reason Provided"):
        """
        Parameters
        -----------
        amount: int
            How many messages should I delete?
        reason: str
            Why am I deleting these?
        """
        channel = ctx.channel
        await ctx.defer()
        messages = [message async for message in ctx.channel.history(limit=amount, before=ctx.message)]
        await channel.delete_messages(messages, reason=reason)
        await ctx.send(f'Deleted {len(messages)} messages with the reason {reason}!', allowed_mentions=discord.AllowedMentions.none())

    @commands.hybrid_command(name="modnick", description='Moderate a users nickname')
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def modnick(self, ctx, user: discord.Member):
        """
        Parameters
        -----------
        user: discord.Member
            Whose nickname needs to be moderated?
        """
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

async def setup(bot):
    await bot.add_cog(utility(bot))