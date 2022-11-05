import discord
from discord.ext import commands
import os

from help_cog import HelpCog
from music_cog import MusicCog

bot = commands.Bot(command_prefix='#', intents=discord.Intents.all())
bot.remove_command('help')
bot.remove_command('leave')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='#play 🏳️‍🌈'))
    print(f'Connected as {bot.user}')

bot.add_cog(HelpCog(bot))
bot.add_cog(MusicCog(bot))

bot.run(str(os.getenv('TOKEN')))
