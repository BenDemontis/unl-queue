import asyncio
import datetime
import json
import os
import random
import time
from discord import Object
import discord
from discord.ext import commands, tasks
from discord import app_commands
import dotenv
import pytz
from utils.find_summoner import find_summoner
from utils.get_match_history import get_match_history
from utils.report_game import report_game

#Loads environment variables such as API tokens, server ID, channel id's
dotenv.load_dotenv()
intents = discord.Intents.all()

#Defines the bot class with the APP_ID from environment and intents setup in the __init__ definition
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.', intents = intents, application_id = int(os.getenv("APP_ID")))
        
    #Does nothing
    async def setup_hook(self):
        pass
    #Every 15 seconds, refresh loaded copy of unlq json. if dev_mode is true close the queue. 
    #If it is the right time of day, open the queue automatically, setting dev mode to false, writing out the current data in unlq json.        
    @tasks.loop(minutes=0.25)
    async def background_task(self):
        with open('C:\\DATA\\unlq.json', 'r') as file:
            unlq = json.load(file)
        if unlq['dev_mode'] == True:
            now = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp(), pytz.timezone('Europe/London'))
            if 0 <= now.weekday() <= 4:
                if datetime.time(19) <= now.time() <= datetime.time(22):
                    print("Opening queue...")

                    unlq['dev_mode'] = False
                    #When devmode is set to false in the json, dumps the information from unlq into the unlq json file.
                    with open('C:\\DATA\\unlq.json', 'w') as unlq_file:
                        json.dump(unlq, unlq_file)
                    #Sets up the server and channels for the bot to access and read from.
                    guild = await self._bot.fetch_guild(int(os.getenv("SERVER_ID")))
                    role = discord.utils.get(guild.roles, id = 676740137815900160)
                    channel = await self._bot.fetch_channel(int(os.getenv("QUEUE")))
                    await channel.set_permissions(role, read_messages=True)
                    channel = await self._bot.fetch_channel(int(os.getenv("LIVE")))
                    await channel.set_permissions(role, read_messages=True)
                    #Sets devmode to false for the actual bot
                    self.queue.devmode = False
                    #Must be awaited because new_lobby() is an asyncio coroutine function that must be called with await.
                    await self.queue.new_lobby()

    #When the bot is ready, start the background task, import the extension cogs, sync commands for the bot to discord.
    async def on_ready(self):
        self.background_task.start()
        for fn in os.listdir("./cogs"):
            if fn.endswith(".py"):
                await bot.load_extension(f'cogs.{fn[:-3]}')
        await self.tree.sync(guild = discord.Object(int(os.getenv("SERVER_ID"))))
#Instantiate bot
bot = MyBot()
#Upon a bot event (i.e. message)
@bot.event
async def on_message(message):
    #If the message is in queue channel and not from the bot
    if message.channel.id == int(os.getenv("QUEUE")) and message.author.id != bot.user.id:
        #Process the commands
        await bot.process_commands(message)
        try:
            #Delete the processed message once complete
            await message.delete()
        except:
            #If processing of the command failed, don't delete the message and do nothing.
            pass
#Import the token for the bot.
asyncio.run(bot.run(os.getenv("TOKEN")))
