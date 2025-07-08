from discord.ext import commands

class listener(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore bot messages
        # Process commands here, only in one cog, not in the main bot file
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(listener(bot))