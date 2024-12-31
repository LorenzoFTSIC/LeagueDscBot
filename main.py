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
    returnedJSON = response.json()
    playerPUUID = returnedJSON.get("puuid", None)
    return playerPUUID

def getMatch():
    pass

@client.event 
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    playerPUUID = getPUUID()
    if playerPUUID:
        print("PUUID acquired: " + playerPUUID)
    else:
        print("Failed to fetch PUUID")


@client.event 
async def on_message(message):
    playerPUUID = getPUUID()
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        print("replying Hello")
        await message.channel.send("Hello!")
    if message.content.startswith("$puuid"):
        if playerPUUID:
            await message.channel.send("Ashkon's PUUID is: " + playerPUUID)
        else:
            print("Failed to fetch PUUID")
            await message.channel.send("Failed to fetch PUUID")


client.run(discordToken)
