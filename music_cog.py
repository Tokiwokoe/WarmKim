import discord
from discord.ext import commands
from youtube_dl import YoutubeDL


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.played_tracks = []

        # ffmpeg and youtube_dl options
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.vc = None

    def youtube_search(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info('ytsearch:%s' % item, download=False)['entries'][0]
                return {'source': info['formats'][0]['url'], 'title': info['title']}
            except Exception as err:
                print(err)
                return False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            self.played_tracks.append(self.music_queue[0][0]['title'])
            self.music_queue.pop(0)

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

            self.played_tracks.append(self.music_queue[0][0]['title'])
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name='play', aliases=['p'], help='Plays a selected track from YouTube')
    async def play(self, ctx, *args):
        query = ''.join(args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send('Connect to a voice channel!')
        else:
            track = self.youtube_search(query)
            if isinstance(track, bool):
                await ctx.send('Could not download the track. Incorrect format. '
                               'This could be due to playlist or a livestream format.')
            else:
                await ctx.send(f"Track added to the queue:\n{track['title'].strip()}")
                self.music_queue.append([track, voice_channel])

                if self.is_playing is False:
                    await self.play_music(ctx)

    @commands.command(name='pause', help='Pauses the current track being played')
    async def pause_command(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.send(f'Track paused by {ctx.author}')
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
            await ctx.send(f'Track resumed by {ctx.author}')

    @commands.command(name='resume', aliases=['r'], help='Resumes playing with the discord bot')
    async def resume_command(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
            await ctx.send(f'Track resumed by {ctx.author}')

    @commands.command(name='skip', aliases=['s'], help='Skips the current track being played')
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            await ctx.send(f'Skipped by {ctx.author}')
            await self.play_music(ctx)

    @commands.command(name='queue', aliases=['q'], help='Displays all of tracks in queue')
    async def queue(self, ctx):
        track_list = ''
        for i in range(0, len(self.music_queue)):
            if i == 0:
                track_list = f'Current track: {self.played_tracks[-1]}\n'
            track_list += str(i+1) + '. ' + self.music_queue[i][0]['title'] + '\n'

        if track_list != '':
            await ctx.send(track_list)
        else:
            await ctx.send(f'Current track: {self.played_tracks[-1]}\n'
                           f'No music in queue')

    @commands.command(name='clear', aliases=['c'], help='Stops the music and clears the queue')
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send('Music queue cleared')

    @commands.command(name='leave', aliases=['disconnect', 'kick', 'd', 'l', 'k'], help='Kick the bot from voice chat')
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name='track', aliases=['t'], help='Display current track playing')
    async def track(self, ctx):
        await ctx.send(f"Current track:\n{self.played_tracks[-1]}")
