import os
import yt_dlp
import discord
import asyncio

from discord.ext import commands

class MusicManager(discord.voice_client.VoiceClient):

    song_queue = []
    song_names = []
    song_durations = []
    primary_text_channel = None

    

    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            'outtmpl': '/Music/%(id)s.%(ext)s'
        }
        


    async def enqueue(self, song):
        path = ""
        custom_title = False

        if not song.startswith('https://'):
            song = (f'ytsearch:{song}')
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                file = ydl.extract_info(song, download=True)
                path = str("Music\\" + file['entries'][0]['id']) + ".mp3"
                custom_title = True
                self.song_names.append(file['entries'][0]['title'])
                self.song_durations.append(float(file['entries'][0]['duration']))
        else:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                file = ydl.extract_info(song, download=True)
                path = str("Music\\" + file['id']) + ".mp3"
                self.song_names.append(file['title'])
                self.song_durations.append(float(file['duration']))

            print(path) #debug

        self.song_queue.append(path)
        print(f"Queue Length: {len(self.song_queue)}") #debug

        if len(self.song_queue) == 1: 
            await self.handle_audio(path)
        
        if custom_title == True: 
            self.song_names.append('[' + file['entries'][0]['title'] + ']')
        else:
            self.song_names.append('[' + file['title'] + ']')


    async def get_next(self):
        if len(self.song_queue) > 0:
            await self.handle_audio(self.song_queue[0])        


    def end_song(self, path, audio_source):
        if not self.is_playing():
            self.song_queue.pop(0)
            audio_source.cleanup()
            os.remove(path)
            

    async def handle_audio(self, path):
        audio_source = discord.FFmpegPCMAudio(path)
        await self.primary_text_channel.send(f'Now playing: {self.song_names[0]}')

        self.play(audio_source)
        self.source = discord.PCMVolumeTransformer(self.source, 1)
        await asyncio.sleep(self.song_durations[0]+2)

        self.song_queue.pop(0)
        audio_source.cleanup()
        os.remove(path)

        if len(self.song_queue) > 0:
            await self.get_next()



    
    async def skip(self):
        self.stop()