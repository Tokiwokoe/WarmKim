import discord
import os
import youtube_dl
import asyncio

client = discord.Client()

voice_clients = {}

YT_DL_OPTIONS = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(YT_DL_OPTIONS)

FFMPEG_OPTIONS = {'options': '-vn'}


@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')


@client.event
async def on_message(msg):
    if msg.content.lower().startswith('#play'):
        try:
            url = msg.content.split()[1]
            print(url)

            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **FFMPEG_OPTIONS)

            voice_client.play(player)
        except Exception as err:
            print(err)
    elif msg.author != client.user:
        if msg.content.lower().startswith('#hi'):
            await msg.channel.send(f'Hi, {msg.author.display_name}')


client.run(os.getenv('TOKEN'))
