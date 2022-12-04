
from pprint import pp
from asyncio import sleep
from urllib.request import urlopen
import os
import json
import dotenv

dotenv.load_dotenv()

def get_rank(summoner_id):
        with urlopen("https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(summoner_id, os.getenv("RIOT_API_KEY"))) as file:
            ranks = json.loads(file.read().decode())
            for rank in ranks:
                if rank['queueType'] == "RANKED_SOLO_5x5":
                    return f"{rank['tier']} {rank['rank']}"


with open('C:\\DATA\\unlq.json', 'r') as unlq:
    unlq = json.load(unlq)

ranks = []
for player in unlq['players'].keys():
    rank = {unlq['players'][player]['discord_name']: get_rank(unlq['players'][player]['id'])}
    ranks.append(rank)
    pp(rank)
    sleep(3)
    
with open('C:\\DATA\\ranks.json', 'w') as ranks_file:
    json.dump(ranks, ranks_file)