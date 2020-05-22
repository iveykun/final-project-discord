import asyncio
import functools
import itertools
import math
import random
import ffmpeg
import time
from datetime import datetime, timedelta
#import os
#from threading import Timer
#from dotenv import load_dotenv
import discord
#from ctypes.util import find_library
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
token = '' #SHOULD BE REDACTED

'''This bot is horribly complicated to setup, you need stuff like FFmpeg, discord.py[voice], youtube-dl... setup in your computer... without mentionning the complicated things you need to do to get a bot license (developer license basically) and a bot token from discord. I need to set paths and stuff manually, since using pip install doesn't seem to work. At first I tested a version with just the birthday functions which I hosted on my raspberry pi at home, and it worked perfectly fine, but once I started adding all those new dependencies it started going crazy (raspi uses python 2.7 by default so maybe my installation of 3.7 was broken) so I had to manually get FFmpeg from their website, unzip it and set the PATH in windows. During my testing on raspi I also discovered that it couldn't read multiple files, so I had to scrap the idea of a dot env and a separate birthday list .txt. Originally the token of my bot would be stored securely in a .env, with the birthdays file having redundant copies to avoid overwriting, but here we are with a list and a string lmao. Another peoblem that I had to face was the lack of f-strings... I never knew it was such a recent implementation, causing me hours of pain trying to figure out why my bot didn't work. Again, raspi running python 2.7 sucks. Originally, the idea was to use threading and timers to make the bot run birthday() once every 24 hours, but I found it simpler to just set up a crontab in raspi and set a timeout of around 23 hours. After I moved to windows, I simply set up a task scheduler to run at the same time every day so it can announce birthdays. To setup the dependencies and stuff like YTDL, I was greatly inspired by the official documentation on said libraries. In fact, i'm using their default settings, which are all copy pasted straight from their github lol. The hardest part was to deal with different versions. Dependencies are so complicated it drives me crazy. Discord.py has a version 0 and version 1, which are called async and rewrite respectively. Version 0, which is what I used at first because of the tutorials on youtube, is not supported anymore by most dependencies, and would require me to downgrade my packages. That's when I switched to rewrite (version 1.0) which made it even more complicated because I didn't know which version was the ones that are supported... Which is why I migrated everything to Windows. On raspi, without a micro HDMI cable I can't do shit. Had to use FireZilla FTP to transfer files and some chrome extension SSH to run the code, and nano is a horrible text editor (ctrl+k for cut??? really? and ctrl+c doesn't work?????). Usually most of my apps are made for windows, but a bot that needs to be online 24/7 was a nice thing to host on my raspi which was gathering dust anyway... I regret infinitely ever thinking that programming on a raspi would be as easy as on windows. I was so happy when it started working at 240am... I never want to touch this ever again and hope it never breaks. Amen.'''


#not sure it works anymore because a python program can't save itself, it has to be saved manually
praisecount = 12

#stolen from the official gitbhub, those are the recommended settings.
class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    #documentation is really great because it saves me he bulk of the work

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t find any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now singing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect', 'begone'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('I am not in any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume at which I am singing"""

        if not ctx.voice_state.is_playing:
            return await ctx.send('I am not singing at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send('I am singing at {}% volume'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing', 'np'])
    async def _now(self, ctx: commands.Context):
        """Displays the song I am singing"""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the current song."""

        if  ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    #@commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')



    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('You haven\'t requested other songs')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)


    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('I am not singing at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        """Sings a song.
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('I can\'t understand this... {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You have to join a voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('I am already in a voice channel.')

    @commands.command(name='setbday')
    async def setbday(self, ctx: commands.Context, date=time.strftime('%m%d')): #if no argument is given, sets today
        """Set bday in the format |setbday MMDD"""

        #bday = (ctx.author)
        f = open("birthdayFile.txt", 'a+')
        bday = str(ctx.author)
        #print("2")
        datee = str(date)
        #print("3")
        #check the pre-made list
        bdays = maker()
        for row in bdays:
            if bday in row:
                await ctx.channel.send("Your birthday is {}".format(str(row)))
                return
        #print("4")
        #skips a line
        bdayy = (datee + ' ' + bday + '\n')
        #print("5")
        f.write(bdayy)
        f.close()
        ###for use in raspi V
        bdays.append(bdayy)

        print("Added to database:", datee, bday)
        await ctx.channel.send("Added to database: {} {}".format(datee, bday))

    @commands.command(name='ping')
    async def ping_(self, message):
        await message.channel.send('Pong!')

    @commands.command(name='good')
    async def good_(self, message):
        global praisecount
        praisecount += 1
        await message.channel.send('Thank you for your praise!')
        #await message.channel.send('I have been praised', praisecount, 'times!')

    @commands.command(name='praise')
    async def praise_(self, message):
        global praisecount
        #praisecount += 1
        #await message.channel.send('Thank you for your praise!')
        await message.channel.send('I have been praised {} times!'.format(str(praisecount)))

    @commands.command(name='clever')
    async def clever_(self, message):
        global praisecount
        praisecount += 1
        await message.channel.send('Homete homete!')
        #await message.channel.send('I have been praised', praisecount, 'times!')

    @commands.command(name='time')
    async def time_(self, message):
        await message.channel.send(time.strftime('%R'))

    @commands.command(name='happy')
    async def hbd_(self, message):
        await message.channel.send('Happy Birthday!')

    @commands.command(name='date')
    async def date_(self, message):
        today = time.strftime('%m%d')
        await message.channel.send('It is {}'.format(str(today)))

    @commands.command(name='help')
    async def help_(self, message):

        await message.channel.send('ping praise clever time happy date help play pause resume leave')
        await message.channel.send('I announce birthdays everyday at 11:15')

bot = commands.Bot(';', description='I am the cutest Eevee, who sings and dances for you! Prefix is ;')
bot.add_cog(Music(bot))


@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))
    await birthday()

#to generate a list that python can read without going crazy, as well as increase the compatibility between windows and raspi

def maker():
    a_file = open("birthdayFile.txt", "r")
    bdays = []
    for line in a_file:
        stripped_line = line.strip()

        bdays.append(stripped_line)

    a_file.close()
    return bdays

async def birthday():
    # set to the test server
    channel = bot.get_channel(-----PUT YOUR CHANNEL HERE !!!------)
    #fileName = open("birthdayFile.txt", 'r')
    bdays = maker()

    today = time.strftime('%m%d')
    for line in bdays:
    #for line in fileName:
        if today in line[0:4]:
            print(today, line)
            line = line.split(' ')
            line[-1] = line[-1].strip()
            if line[-1] != line[1]:
                bdayperson = line[1]+' '+line[2]
            else:
                bdayperson = line[1]
            await channel.send(f"Happy birthday to "+ bdayperson + "! 🎈🎉" )


bot.run(token)
