import discord
from discord import PCMVolumeTransformer, FFmpegPCMAudio
from discord.ext import commands
import youtube_dl as ydl


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.queue = [] 

        self.YDL_OPTIONS = {'format': 'bestaudio'}
        self.FFMPEG_OPTIONS = {'options': '-vn',
                               'before_options': '-reconnect 1 -reconnect_streamed 1'}
        
    # searches youtube for requested song and return the link address
    def search(self, song_title):
        info = ydl.YoutubeDL(self.YDL_OPTIONS).extract_info(f"ytsearch:{song_title}", download=False)
        
        return {'title': info['entries'][0]['title'], 'link': info['entries'][0]['formats'][0]['url']}

    # checks if queue is empty
    async def check_queue(self, ctx):
        if len(self.queue) > 0:
            song = self.queue.pop(0)
            await self.play_song(ctx, song)
        else:
            await self.disconnect(ctx)

    # plays requested songs
    async def play_song(self, ctx, song):
        url = song['link']
        await ctx.send(f"Now playing {song['title']}")
        ctx.voice_client.play(PCMVolumeTransformer(FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)), 
                        after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))

    # searches for requested songs and adds to queue if already playing one
    @commands.command()
    async def play(self, ctx, *args):
        if ctx.author.voice is None:
            return await ctx.send("You must be in a voice channel first.")
        query = " ".join(args)

        song = self.search(query)

        url = song['link']

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        if ctx.voice_client.is_playing() is True:
            self.queue.append(song)
            await ctx.send("Song added to Queue.")
            return None
        
        await self.play_song(ctx, song)

    # skip current song
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("No song to skip.")
        
        await ctx.send("Skipping song")
        ctx.voice_client.stop()

    # pause current song that is playing
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("No song to pause.")
        await ctx.send("Music paused. Type !resume to play.")
        await ctx.voice_client.pause()

    # resume a paused song
    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("No song to resume.")
        await ctx.voice_client.resume()

    # disconnect bot from voice channel
    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client:
            return await ctx.voice_client.disconnect()
        await ctx.send("I am not in a channel.")
        


# adds the cog to our bot
def setup(client):
    client.add_cog(Music(client))
    