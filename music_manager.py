import os
import yt_dlp
import discord
import time

from discord.ext import commands

class MusicManager(discord.voice_client.VoiceClient):

    song_queue = []

    def __init__(self, client, channel):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            'outtmpl': '/Music/%(id)s.%(ext)s'
        }
        super().__init__(client, channel)


    async def enqueue(self, song):
        path = ""
        custom_title = False
        if not song.startswith('https://'):
            song = (f'ytsearch:{song}')
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                file = ydl.extract_info(song, download=True)
                path = str("Music\\" + file['entries'][0]['id']) + ".mp3"
                custom_title = True
        else:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                file = ydl.extract_info(song, download=True)
                path = str("Music\\" + file['id']) + ".mp3"

            print(path) #debug

        self.song_queue.append(path)
        print(f"Queue Length: {len(self.song_queue)}") #debug

        if len(self.song_queue) == 1: 
            self.begin_audio(path)
        
        if custom_title == True: 
            return str('[' + file['entries'][0]['title'] + ']')

        return str('[' + file['title'] + ']')


    def get_next(self, path):
        if len(self.song_queue) > 0:
            self.begin_audio(self.song_queue[0])        


    def end_song(self, path, audio_source):
        if not self.is_playing():
            print("end song called")
            self.song_queue.pop(0)
            print(f"Queue Length: {len(self.song_queue)}") #debug
            self.get_next(path)
            audio_source.cleanup()
            os.remove(path)


    def begin_audio(self, path):
        audio_source = discord.FFmpegPCMAudio(path)

        self.play(audio_source, after=lambda x: self.end_song(path, audio_source))
        self.source = discord.PCMVolumeTransformer(self.source, 1)

    
    def skip(self):
        self.stop()