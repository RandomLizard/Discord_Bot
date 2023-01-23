import os
import discord
import music_manager as MM

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.all()

client = commands.Bot(intents=intents,command_prefix='!')

active_voice_clients = {}
active_music_managers = {}


async def create_voice_client(ctx, channel):
    """creates voice client in the specified channel with a music manager attached to it"""

    voice_client = await channel.connect(cls=discord.voice_client.VoiceClient, self_deaf = True)
    active_voice_clients.update({ctx.guild.id : voice_client})
    attach_music_manager(voice_client)


async def destroy_voice_client(ctx, voice_client):
    (voice_client, mus_manager) = await find_voice_client(ctx)
    await voice_client.disconnect()
    voice_client.cleanup()

    active_music_managers.pop(voice_client)
    active_voice_clients.pop(ctx.guild.id)


def attach_music_manager(voice_client):
    """attaches a music manager to a voice client"""

    mus_manager = MM.MusicManager(voice_client)
    active_music_managers.update({voice_client : mus_manager})


async def find_voice_client(ctx):
    """Finds and returns both the voice client and it's respective music manager for the active server"""

    voice_client = None
    mus_manager = None
    
    if ctx.guild.id in active_voice_clients:
        voice_client = active_voice_clients[ctx.guild.id]
        mus_manager = active_music_managers[voice_client]

    return (voice_client, mus_manager)

async def manage_voice_connection(ctx, command):
    """Manages voice connections for the discord bot. Will respond snarkily if 
    you try to summon it to a place it can't go."""

    user_voice = ctx.author.voice #The command caller's voice status
    (voice_client, mus_manager) = await find_voice_client(ctx)

    if command == 'connect':

        if voice_client != None:
            await voice_client.move_to(user_voice.channel)

        if user_voice != None and voice_client == None:
            await create_voice_client(ctx,user_voice.channel)
        else:
            await ctx.send("You're not in a voice channel you dingus.")

    elif command == 'disconnect':

        if voice_client != None:
            await destroy_voice_client(ctx, voice_client)

        else:
            await ctx.send("I'm not connected here you dope")        
    else:
        print("if you see this, God help you.")


@client.command()
async def connect(ctx):
    await manage_voice_connection(ctx, 'connect')


@client.command()
async def disconnect(ctx):
    await manage_voice_connection(ctx, 'disconnect')


@client.command()
async def clearchannel(ctx):
    await ctx.channel.purge()


@client.command()
async def play(ctx, *input):
    
    (voice_client, mus_manager) = await find_voice_client(ctx)
    print(voice_client)
    print(mus_manager)
    
    if voice_client == None:
        await manage_voice_connection(ctx, 'connect')
    else:
        query = ' '.join(input)

        song_title = await mus_manager.enqueue(query)

        if len(mus_manager.song_queue) > 1:
            await ctx.send(f'Your song, {song_title} is # {len(mus_manager.song_queue)} in the queue.')


@client.command()
async def skip(ctx):
    (voice_client, mus_manager) = await find_voice_client(ctx)


    if voice_client != None:
        mus_manager.skip()


@client.command()
async def pause(ctx):
    (voice_client, mus_manager) = await find_voice_client(ctx)

    if voice_client != None: 
        mus_manager.pause()


@client.command()
async def resume(ctx):
    (voice_client, mus_manager) = await find_voice_client(ctx)

    if voice_client != None:
        mus_manager.resume()


client.run(TOKEN)