import discord
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env
load_dotenv()
discordToken = os.getenv("DISCORDTOKEN")
riotToken = os.getenv("RIOTTOKEN")

class GwenBot:
    def __init__(self, discordToken, riotToken):
        # Initialize with the provided tokens
        self.discordToken = discordToken
        self.riotToken = riotToken
        self.player_puuid = None  # Player PUUID will be fetched when needed
        self.client = discord.Client(command_prefix='$', intents=discord.Intents.all())
        
        # Register event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    def getMatch(self):
        if self.player_puuid:
            url =   f"https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{self.player_puuid}?api_key={self.riotToken}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                returned_json = response.json()
                print("Request successful")
                return returned_json
            except requests.exceptions.RequestException as e:
                print(f"Error finding match: {e}")
                return e
        else:
            print("No puuid found")
            return "No puuid found"

    def get_puuid(self):
        #"""Fetches the player's PUUID from Riot Games API."""
        game_name = "Air Coots"
        tag = "Prime"
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}?api_key={self.riotToken}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            returned_json = response.json()
            self.player_puuid = returned_json.get("puuid", None)
            return self.player_puuid
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PUUID: {e}")
            return None

    async def on_ready(self):
        #"""Triggered when the bot has successfully connected to Discord."""
        print(f"We have logged in as {self.client.user}")
        
        # Fetch the PUUID when the bot is ready
        self.get_puuid()
        
        if self.player_puuid:
            print(f"PUUID acquired: {self.player_puuid}")
        else:
            print("Failed to fetch PUUID")

    async def on_message(self, message):
        #"""Triggered when a message is received."""
        if message.author == self.client.user:
            return  # Ignore messages from the bot itself
        
        if message.content.startswith("$hello"):
            print("replying Hello")
            await message.channel.send("Hello!")
        
        if message.content.startswith("$puuid"):
            if self.player_puuid:
                print("Supplying puuid")
                await message.channel.send(f"Ashkon's PUUID is: {self.player_puuid}")
            else:
                print("Failed to fetch PUUID")
                await message.channel.send("Failed to fetch PUUID")
        
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
            else:
                print("Player not found.")

    def run(self):
        #"""Starts the bot and runs the event loop."""
        self.client.run(self.discordToken)


chibiGwen = GwenBot(discordToken,riotToken)
chibiGwen.run()
