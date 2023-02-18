import os
import discord
import music_manager as MM
import json

from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.all()

client = commands.Bot(intents=intents,command_prefix='!')

active_voice_clients = {}

primary_text_channels = {}

#LOAD PRIMARY CHANNELS FOR GUILDS#
json_path = Path('data\\data.json')

try: 
    with open(json_path, "r") as read_file:
        primary_text_channels = json.load(read_file)      

except: 
    print("No json file detected.")


def convert_keys_to_int(dictionary):

    dictionary = {int(k):v for k, v in dictionary.items()}
    return dictionary

primary_text_channels = convert_keys_to_int(primary_text_channels)
print(primary_text_channels)

##TEXT-RELATED FUNCTIONS##

async def find_primary_text_channel(ctx):
    print(primary_text_channels)
    print('Attempting to find primary text channel for this server')
    if ctx.guild.id in primary_text_channels:
        print('FOUND GUILD')
        return await client.fetch_channel(primary_text_channels[ctx.guild.id])
    else:
        print('NOT FOUND')
        return None



##TEXT-RELATED COMMANDS##

@client.command()
async def primarychannel(ctx):
    await ctx.send(f"Assigning [{ctx.channel.name}] as the primary channel that I'll spam.")
    primary_text_channels.update({ctx.guild.id : ctx.channel.id})
    with open(json_path, "w") as write_file:
        json.dump(primary_text_channels, write_file, indent=4)



##MUSIC-RELATED FUNCTIONS##

async def create_voice_client(ctx, channel):
    """creates voice client in the specified channel with a music manager attached to it"""

    primary_text_channel = await find_primary_text_channel(ctx)

    voice_client = await channel.connect(cls=MM.MusicManager, self_deaf = True)
    active_voice_clients.update({ctx.guild.id : voice_client})
    voice_client.primary_text_channel = primary_text_channel
    print(voice_client.primary_text_channel)


async def destroy_voice_client(ctx, voice_client):
    voice_client = await find_voice_client(ctx)
    await voice_client.disconnect()
    voice_client.cleanup()

    active_voice_clients.pop(ctx.guild.id)


async def find_voice_client(ctx):
    """Finds and returns both the voice client and it's respective music manager for the active server"""

    voice_client = None
    
    if ctx.guild.id in active_voice_clients:
        voice_client = active_voice_clients[ctx.guild.id]

    return (voice_client)

async def manage_voice_connection(ctx, command):
    """Manages voice connections for the discord bot. Will respond snarkily if 
    you try to summon it to a place it can't go."""

    user_voice = ctx.author.voice
    voice_client = await find_voice_client(ctx)

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


##MUSIC-RELATED COMMANDS##
@client.command()
async def connect(ctx):
    await manage_voice_connection(ctx, 'connect')


@client.command()
async def disconnect(ctx):
    await manage_voice_connection(ctx, 'disconnect')


@client.command()
async def play(ctx, *input):
    query = ' '.join(input)
    voice_client = await find_voice_client(ctx)
    print(voice_client)
    
    if voice_client == None:
        await manage_voice_connection(ctx, 'connect')
    else:
        primary_text_channel = await find_primary_text_channel(ctx)
        print(primary_text_channel)
        song_title = await voice_client.enqueue(query)


@client.command()
async def skip(ctx):
    voice_client = await find_voice_client(ctx)


    if voice_client != None:
        await voice_client.skip()


@client.command()
async def pause(ctx):
    voice_client = await find_voice_client(ctx)

    if voice_client != None: 
        await voice_client.pause()


@client.command()
async def resume(ctx):
    voice_client = await find_voice_client(ctx)

    if voice_client != None:
        await voice_client.resume()

        


client.run(TOKEN)