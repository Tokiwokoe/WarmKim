import asyncio

from discord.ext import commands
import os

from help_cog import HelpCog
from music_cog import MusicCog

bot = commands.Bot(command_prefix='#')

bot.remove_command('help')

bot.add_cog(HelpCog(bot))
bot.add_cog(MusicCog(bot))

bot.run(str(os.getenv('TOKEN')))
