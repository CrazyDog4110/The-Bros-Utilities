import discord
from discord.ext import commands

# Channels where media-only restriction applies
MEDIA_CHANNEL_IDS = {1232086351093039164}

class MediaOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or isinstance(message.channel, discord.Thread):
            return

        if message.channel.id in MEDIA_CHANNEL_IDS:
            has_media = any(
                a.content_type and a.content_type.startswith(('image/', 'video/'))
                for a in message.attachments
            )

            has_allowed_embed = any(
                (e.type in ('video', 'gifv')) or
                (e.type == 'rich' and e.thumbnail and e.thumbnail.url.endswith('.gif')) or
                (e.url and e.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm')))
                for e in message.embeds
            )

            if not has_media and not has_allowed_embed:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"{message.author.mention} Only image, video, or GIF messages are allowed in this channel.",
                        delete_after=5
                    )
                except discord.Forbidden:
                    print("Missing permissions to delete messages or send warnings.")

async def setup(bot):
    await bot.add_cog(MediaOnly(bot))
