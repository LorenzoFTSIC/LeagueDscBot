import discord
import os
import time
from dotenv import load_dotenv
import requests

load_dotenv()
discordToken = os.getenv("DISCORDTOKEN")
riotToken = os.getenv("RIOTTOKEN")
client = discord.Client(command_prefix='$',intents=discord.Intents.all())

def getPUUID():
    gameName = "ASHKON"
    tag = "fart"
    url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + gameName + "/" + tag + "?api_key=" + riotToken
    response = requests.get(url)
    print(response.json())  
    return response.json()

def getMatch():
    pass

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
        await message.channel.send(getPUUID())
    # await message.channel.send(message)

client.run(discordToken)
