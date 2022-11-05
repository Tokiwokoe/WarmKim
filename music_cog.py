import discord
from discord.ext import commands

from youtube_dl import YoutubeDL


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        self.music_queue = []

        # ffmpeg and youtube_dl options
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vc = None

    def youtube_search(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info('ytsearch:%s' % item, download=False)['entries'][0]
            except Exception as err:
                print(err)

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc is None:
                    await ctx.send('Could not connect to the voice channel')
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name='play', aliases=['p'], help='Plays a selected song from YouTube')
    async def play(self, ctx, *args):
        query = ' '.join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send('Connect to a voice channel!')
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.youtube_search(query)
            if isinstance(song, bool):
                await ctx.send(
                    'Could not download the song. Incorrect format try another keyword. '
                    'This could be due to playlist or a livestream format.')
            else:
                await ctx.send(f"Song added to the queue:\n{song['title'].strip()}")
                self.music_queue.append([song, voice_channel])

                if self.is_playing is False:
                    await self.play_music(ctx)

    @commands.command(name='pause', help='Pauses the current song being played')
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
        self.vc.resume()

    @commands.command(name='resume', aliases=['r'], help='Resumes playing with the discord bot')
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
        self.vc.resume()

    @commands.command(name='skip', aliases=['s'], help='Skips the current song being played')
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(name='queue', aliases=['q'], help='Displays the current songs in queue')
    async def queue(self, ctx):
        retval = ''
        for i in range(0, len(self.music_queue)):
            # display 10 songs in the current queue
            if i > 9:
                break
            retval += str(i+1) + '. ' + self.music_queue[i][0]['title'] + '\n'

        if retval != '':
            await ctx.send(retval)
        else:
            await ctx.send('No music in queue')

    @commands.command(name='clear', aliases=['c'], help='Stops the music and clears the queue')
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send('Music queue cleared')

    @commands.command(name='leave', aliases=['disconnect', 'l', 'd'], help='Kick the bot from VC')
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
