from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = '''
```
General commands:
#help - Displays all the available commands
#play <keywords> - Finds the song on youtube and plays it in your current channel
#pause - Pauses the current song being played or resumes if already paused
#resume - Resumes playing the current song
#queue - Displays the current music queue
#skip - Skips the current song being played
#clear - Stops the music and clears the queue
#leave - Disconnected the bot from the voice channel
```
'''
        self.text_channel_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

    @commands.command(name='help', help='Displays all the available commands')
    async def help(self, ctx):
        await ctx.send(self.help_message)
