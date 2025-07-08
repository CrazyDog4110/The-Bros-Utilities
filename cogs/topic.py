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
import random
from discord.ext import commands

starters = {
    1: "What's your favorite game of all time?",
    2: "Have you ever finished a game 100%?",
    3: "What's the most underrated game you've played?",
    4: "Favorite gaming console or platform?",
    5: "What's your dream gaming setup?",
    6: "If you could live in a game's universe, which one would it be?",
    7: "Favorite indie game?",
    8: "What's the funniest gaming glitch you've encountered?",
    9: "Which game has the best soundtrack?",
    10: "PC gaming or console gaming?",
    11: "What's the last movie you watched?",
    12: "Favorite movie genre?",
    13: "Which TV show are you currently binge-watching?",
    14: "Who is your favorite movie villain?",
    15: "If you could live in a TV show universe, which one?",
    16: "What's the best movie soundtrack you've heard?",
    17: "Marvel or DC?",
    18: "Have you ever walked out of a movie theater? Why?",
    19: "Favorite animated movie?",
    20: "What's the most underrated TV show in your opinion?",
    21: "What's your favorite band or artist?",
    22: "What song is currently stuck in your head?",
    23: "Do you play any musical instruments?",
    24: "What's the best concert you've ever attended?",
    25: "What's your go-to karaoke song?",
    26: "Favorite music genre?",
    27: "Which album could you listen to on repeat forever?",
    28: "What's the most overplayed song right now?",
    29: "Vinyl, CDs, or streaming?",
    30: "Who's an artist you'd love to see live?",
    31: "What's the coolest gadget you own?",
    32: "Apple or Android?",
    33: "Which piece of tech has changed your life the most?",
    34: "What's your favorite app or software?",
    35: "Do you prefer dark mode or light mode?",
    36: "What tech invention are you looking forward to?",
    37: "How do you organize your digital files?",
    38: "VR gaming: Yay or nay?",
    39: "What's the oldest piece of tech you still use?",
    40: "Have you ever built your own PC?",
    41: "What's your favorite type of cuisine?",
    42: "What's the weirdest food you've tried?",
    43: "Pineapple on pizza: Yes or no?",
    44: "What's your comfort food?",
    45: "Favorite dessert?",
    46: "Coffee or tea?",
    47: "Do you enjoy cooking or baking?",
    48: "What's your favorite snack for gaming or watching movies?",
    49: "What's a dish you'd love to learn how to make?",
    50: "Favorite fast-food chain?",
    51: "What's your favorite book or series?",
    52: "Who is your favorite author?",
    53: "What's a book you couldn't finish?",
    54: "E-books or physical books?",
    55: "Do you prefer fiction or non-fiction?",
    56: "Which fictional character do you relate to the most?",
    57: "Have you ever read a book in one sitting?",
    58: "What's a book you think everyone should read?",
    59: "What genre do you enjoy the most?",
    60: "What's the last book you read?",
    61: "What's your dream travel destination?",
    62: "Do you prefer mountains or beaches?",
    63: "What's the most beautiful place you've visited?",
    64: "Favorite road trip memory?",
    65: "What's a country you'd love to visit but haven’t yet?",
    66: "Do you prefer city life or countryside?",
    67: "What's the best local cuisine you've tried while traveling?",
    68: "Favorite travel companion?",
    69: "What's the most interesting cultural experience you've had?",
    70: "What's your favorite mode of travel: plane, train, or car?",
    71: "If you could have any superpower, what would it be?",
    72: "What's your favorite meme?",
    73: "Cats or dogs?",
    74: "What's the most ridiculous thing you've bought online?",
    75: "If you could time travel, which era would you visit?",
    76: "What's your favorite childhood memory?",
    77: "If you could instantly master a skill, what would it be?",
    78: "What's your spirit animal?",
    79: "What's your most useless talent?",
    80: "What’s a conspiracy theory you find intriguing?",
    81: "Who's your favorite celebrity?",
    82: "What's the best concert you've ever seen?",
    83: "Do you follow any YouTubers or streamers?",
    84: "What's the most iconic pop culture moment you remember?",
    85: "What’s your guilty pleasure TV show or movie?",
    86: "Which fictional universe would you live in?",
    87: "What's a trend you think should make a comeback?",
    88: "Do you enjoy any reality TV shows?",
    89: "Favorite childhood cartoon?",
    90: "What's the most nostalgic song for you?",
    91: "Do you have any hobbies?",
    92: "What's a skill you're trying to learn?",
    93: "Do you enjoy any creative activities like drawing or writing?",
    94: "What sports or activities do you enjoy?",
    95: "What's the most rewarding hobby you have?",
    96: "Do you enjoy collecting anything?",
    97: "What's your favorite board game or card game?",
    98: "How do you usually spend your weekends?",
    99: "What’s a hobby you’ve always wanted to pick up?",
    100: "Do you prefer outdoor or indoor activities?",
}

class topic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='topic', description="Generate a topic")
    @commands.has_permissions(manage_messages=True)
    async def topic(self, ctx, channel: discord.channel.TextChannel=None):
        if channel is None:
            channel = ctx.channel  # Default to the channel where the command was invoked
        random_starter = random.choice(starters)
        await channel.send(f"# {random_starter}")
    
    @app_commands.command(name='topic', description="Generate a topic")
    #@app_commands.describe(channel="What channel should I send the topic to?")
    @app_commands.default_permissions(manage_messages=True)
    async def slash_topic(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """
        Parameters
        -----------
        channel: discord.TextChannel
            What channel should I send the topic to?
        """
        if channel is None:
            channel = interaction.channel  # Default to the channel where the command was invoked

        random_starter = random.choice(starters)
        await channel.send(f"# {random_starter}")
        await interaction.response.send_message("Sent!", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(topic(bot))
