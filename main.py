import discord
import os
import time
from dotenv import load_dotenv

load_dotenv()
myToken = os.getenv("DISCORDTOKEN")
client = discord.Client(command_prefix='$',intents=discord.Intents.all())

@client.event 
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event 
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        print("replying Hello")
        await message.channel.send("Hello!")
    # await message.channel.send(message)

client.run(myToken)
