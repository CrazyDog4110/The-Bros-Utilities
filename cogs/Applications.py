import discord 
from discord.ext import commands
from discord import ui

class applications(commands.Cog):
    guild = None
    def __init__(self, bot):
        self.bot = bot
        self.in_app = []

    class AppViews(ui.View):
        def __init__(self, bot, user, timeout=9999999999):  # Default timeout is 600 seconds (10 minutes)
            super().__init__(timeout=timeout)
            self.bot = bot
            self.user = user
            self.message = None
        
        @ui.button(label="Approve", style=discord.ButtonStyle.green)
        async def approve(self, interaction: discord.Interaction, button: ui.Button):
            # Action when the "Approve" button is clicked
            await interaction.response.send_message(f"{self.user.mention} has been approved as a moderator!", ephemeral=False)
            await self.user.send("You have been approved for moderator!")
            guild = self.bot.get_guild(1081122313870778471)
            tmod = guild.get_role(1224549822162403360)
            await guild.get_member(self.user.id).add_roles(tmod)
            self.stop()

        @ui.button(label="Deny", style=discord.ButtonStyle.red)
        async def deny(self, interaction: discord.Interaction, button: ui.Button):
            await interaction.response.send_message(f"{self.user.mention}'s application has been denied.", ephemeral=False)
            await self.user.send("You have been denied for moderator!")
            self.stop()
        
        async def on_timeout(self):
            # Disable buttons after timeout
            for child in self.children:
                child.disabled = True
            if self.message:
                await self.message.edit(content="This application has timed out.", view=self)
            print("View timed out")
    
    class ApplicationSelect(discord.ui.Select):
        def __init__(self, parent_cog, bot):
            self.parent_cog = parent_cog  # Save parent_cog
            self.bot = bot
            options = [
                discord.SelectOption(label="Moderator Application", emoji="🔨", description="Apply for Moderator!", value="thebrosmod"),
            ]
            # Initialize the parent Select class with the options
            super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)
        
        async def callback(self, interaction: discord.Interaction):
            value = self.values[0]
            if value == "thebrosmod":
                user = interaction.user
                guild = self.bot.get_guild(1081122313870778471)
                for role in guild.get_member(user.id).roles:
                    if role.id == 1224662390453436547:
                        await interaction.response.send_message("You are already a staff member")
                        return
                
                self.parent_cog.in_app.append(user.id)
                await interaction.response.send_message(content="Starting application process, if you want to cancel at any time say `.cancel`")
                await user.send(content="How old are you?")
                Age = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if Age.content.lower() == '.cancel':
                    await user.send("Application process has been cancelled.")
                    self.parent_cog.in_app.remove(user.id)
                    return
                await user.send(content="Why do you want to be a moderator here?")
                Why = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if Why.content.lower() == '.cancel':
                    await user.send("Application process has been cancelled.")
                    self.parent_cog.in_app.remove(user.id)
                    return
                await user.send(content="How much can you moderate per day?")
                what = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if what.content.lower() == '.cancel':
                    await user.send("Application process has been cancelled.")
                    self.parent_cog.in_app.remove(user.id)
                    return
                await user.send(content="Do you understand that you must provide proof for moderation actions? Ways to provide proof are in the staff guidelines, which you can access if you get accepted for mod.")
                proof = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if what.content.lower() == '.cancel':
                    await user.send("Application process has been cancelled.")
                    self.parent_cog.in_app.remove(user.id)
                    return
                await user.send(content="Do you understand that the rules also apply to you as mod?")
                rules = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if what.content.lower() == '.cancel':
                    await user.send("Application process has been cancelled.")
                    self.parent_cog.in_app.remove(user.id)
                    return
                await user.send(content="What timezone are you in?")
                time = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if time.content.lower() == '.cancel':
                    await user.send("Application process has been cancelled.")
                    self.parent_cog.in_app.remove(user.id)
                    return
                await user.send("Thank you for your application! Here are your responses:\n"
                                f"Age: {Age.content}\n"
                                f"Why you want to be a mod: {Why.content}\n"
                                f"How active you are: {what.content}\n"
                                f"Do you understand the proof requirement: {proof.content}\n"
                                f"Do you understand the rules still apply: {rules.content}\n"
                                f"Your Timezone: {time.content}")
                self.parent_cog.in_app.remove(user.id)
                channel = self.bot.get_channel(1224550220721815564)
                view = self.parent_cog.AppViews(self.bot, user)
                await channel.send(f"{user.mention}'s application for moderator.\n"
                            f"Age: {Age.content}\n"
                            f"Why they want to be a mod: {Why.content}\n"
                            f"How active they are: {what.content}\n"
                            f"Do they understand the proof requirement: {proof.content}\n"
                            f"Do they understand the rules still apply: {rules.content}\n"
                            f"Their Timezone: {time.content}", view=view)

    class SelectView(discord.ui.View):
        def __init__(self, parent_cog, *, timeout=9999999999):
            super().__init__(timeout=timeout)
            self.parent_cog = parent_cog
            # Pass the cog instance and bot to ApplicationSelect correctly
            self.add_item(self.parent_cog.ApplicationSelect(self.parent_cog, self.parent_cog.bot))

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            if message.author.id in self.in_app:
                pass
            elif message.author.id == 1285858287404847185:
                return
            else:
                await message.reply(content="Select a form that you would like to fillout.", view=self.SelectView(self))

async def setup(bot):
    await bot.add_cog(applications(bot))
'''view=self.SelectView(self)'''
