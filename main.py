import discord
from discord import app_commands
import os
import json
import asyncio
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
discordToken = os.getenv("DISCORDTOKEN")
riotToken = os.getenv("RIOTTOKEN")

#Open local json for parsing champ data
jsonPath = "champion.json"
with open(jsonPath, "r", encoding="utf-8") as champDatafile:
    champData = json.load(champDatafile)



class GwenBot:
    def __init__(self, discordToken, riotToken):
        # Initialize with the provided tokens
        self.discordToken = discordToken
        self.riotToken = riotToken
        self.player_puuid = None  # Player PUUID will be fetched when needed
        self.client = discord.Client(command_prefix='$', intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self.client)
        self.flag = False
        self.lastMatchID = None
        self.curChampId = None
        self.curChampName = None
        self.gameName = None
        self.gameTag = None
        self.curMatchData = None
        self.postMatchData = None
        
        # Register event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    def getMatch(self):
        if self.player_puuid:
            url =   f"https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{self.player_puuid}?api_key={self.riotToken}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                returnedJson = response.json()
                print("Request successful")
                self.curMatchData = returnedJson
            except requests.exceptions.RequestException as e:
                print(f"Error finding match: {e}")  
                self.curMatchData = None
        else:
            print("No match found")
            return "No match found"

    def getPostMatchData(self):
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{self.lastMatchID}?api_key={self.riotToken}"
        if self.lastMatchID:
            try:
                response = requests.get(url)
                response.raise_for_status()
                # returnedJson = response.json()
                # self.curMatchData = returnedJson
                print("Request successful")
                print(self.postMatchData)
                self.postMatchData = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error finding match: {e}")
        else:
            print("Can't find the last match ID.")

    def postMatchRecap(self):
        print("Updating post match data...")
        self.getPostMatchData()
        for i in self.postMatchData:
            if self.postMatchData[participants][puuid] == self.player_puuid:
                print(self.postMatchData[participants][win])

    def getAccountInfo(self, messageContent):   
        splitMessage = messageContent.replace("$listen ", "")
        print(splitMessage)
        splitMessageList = splitMessage.split("#")
        print(splitMessageList)
        self.gameName = splitMessageList[0]
        self.gameTag = splitMessageList[1]
        print(self.gameName)
        print(self.gameTag)

    def get_puuid(self):
        #"""Fetches the player's PUUID from Riot Games API."""
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.gameName}/{self.gameTag}?api_key={self.riotToken}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            returned_json = response.json()
            self.player_puuid = returned_json.get("puuid", None)
            return self.player_puuid
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PUUID: {e}")
            return None
        
    def findPlayerFromMatch(self, returnedJson):
        for x in returnedJson["participants"]:
            if x["puuid"] == self.player_puuid:
                # print("Player is: ")
                # print(x)
                # print(x["riotId"])
                return x
            
    def setPlayerInfo(self, gameName, gameTag):
        self.gameName = gameName
        self.gameTag = gameTag

    async def on_ready(self):
        #"""Triggered when the bot has successfully connected to Discord."""
        print(f"We have logged in as {self.client.user}")
        
    async def on_message(self, message):
        #"""Triggered when a message is received."""
        if message.author == self.client.user:
            return  # Ignore messages from the bot itself
        
        if message.content.startswith("$hello"):
            print("replying Hello")
            await message.channel.send("Hello!")

        if message.content.startswith("$update"):
            print("Updating timestamp")
            self.getMatch()
            print(self.curMatchData["gameLength"])
            await message.channel.send("Match has been ongoing for: " + str((self.curMatchData["gameLength"] + 120) // 60) + "minutes and " + str((self.curMatchData["gameLength"] + 120) % 60) + " seconds.")

        if message.content.startswith("$liveMatch"):
            if self.player_puuid:
                print("Player Found")
                returnedJson = self.getMatch()
                print("\nPlayers in match:\n--------------------\n")
                for x in returnedJson["participants"]:
                    if x["puuid"] == self.player_puuid:
                        print("Player is: ")
                        print(x)
                    print(x["riotId"])
                # print(returnedJson)
                print(returnedJson["gameId"])
                # print(returnedJson["participants"])
            else:
                print("Player not found.")

        if message.content.startswith("$listen"):
                    # Fetch the PUUID when the bot is ready
            self.getAccountInfo(message.content)
            self.get_puuid()
        
            if self.player_puuid:
                print(f"PUUID acquired: {self.player_puuid}")
            else:
                print("Failed to fetch PUUID")

            self.flag = True
            if self.player_puuid:
                while (self.flag == True):
                    print("Checking for match...")
                    self.getMatch()
                    # print(self.curMatchData)
                    # await asyncio.sleep(30)
                    if (self.curMatchData):
                        if (self.curMatchData["gameId"] != self.lastMatchID):
                            print("New match in progress updating data...")
                            self.lastMatchID = self.curMatchData["gameId"]
                            print(self.lastMatchID)
                            playerData = self.findPlayerFromMatch(self.curMatchData)
                            self.curChampId = playerData["championId"]
                            print("Player's champ id is: " + str(self.curChampId))
                            ##Move to new function - parses champid
                            for i in champData["data"]:
                                if champData["data"][i]["key"] == str(self.curChampId):
                                    self.curChampName = champData["data"][i]["id"]
                            print("Player is currently playing: " + self.curChampName)

                            await message.channel.send("New match found! Game id:" + str(self.lastMatchID) + ".\nThey're currently playing: " + self.curChampName)
                        else:
                            print("Old match ongoing")
                        await asyncio.sleep(60)
                    else:
                        ## Checks if there is a last match id saved, meaning it's not first game since bot start
                        if (self.lastMatchID):
                            print("Match has ended! They're (probably) queueing again...")
                            self.postMatchRecap()
                        else:
                            print("Looks like they havn't started playing yet!")
                        await asyncio.sleep(60)
            else:
                print("Player not found")
                await message.channel.send("Player not found")

                
        if message.content.startswith("$stopListening"):
            self.flag = False
            await message.channel.send("Chibi Gwen has stopped listening")
            

    def run(self):
        #"""Starts the bot and runs the event loop."""
        self.client.run(self.discordToken)

chibiGwen = GwenBot(discordToken,riotToken)
chibiGwen.run()
