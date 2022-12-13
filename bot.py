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
                    #Start the bot new lobby creation process and pass back the control to the event loop controller.
                    #Why is this here? Wouldn't just calling self.queue.new_lobby() finish the process once the new lobby is made anyways and pass back control since the function is complete.
                    await self.queue.new_lobby()
    
    async def on_ready(self):
        self.background_task.start()
        for fn in os.listdir("./cogs"):
            if fn.endswith(".py"):
                await bot.load_extension(f'cogs.{fn[:-3]}')
        await self.tree.sync(guild = discord.Object(int(os.getenv("SERVER_ID"))))

bot = MyBot()

@bot.event
async def on_message(message):
    if message.channel.id == int(os.getenv("QUEUE")) and message.author.id != bot.user.id:
        await bot.process_commands(message)
        try:
            await message.delete()
        except:
            pass

asyncio.run(bot.run(os.getenv("TOKEN")))
