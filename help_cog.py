from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = '''
```
General commands:
--------------------------------------------------------------------------------------------
#help, #h - Display all the available commands.
#play, #p <keywords> - Find the track on YouTube and play it in your current voice channel.
#pause - Pause the current track being played or resume if already paused.
#resume, #r - Resume playing the current track.
#queue, #q - Display the current queue.
#skip, #s - Skip the current track being played.
#clear, #c - Stop the music and clear the queue.
#leave, #disconnect, #kick, #l, #d, #k - Disconnect the bot from the voice channel.
#track, #t - Display the current track.
--------------------------------------------------------------------------------------------
```
'''

    @commands.command(name='help', aliases=['h'], help='Displays all the available commands')
    async def help(self, ctx):
        await ctx.send(self.help_message)
