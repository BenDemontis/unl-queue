import os
import json

games = []
for fn in os.listdir("C:\\DATA\\games"):
        with open(f'C:\\DATA\\games\\{fn}', 'r') as file:
            game = json.load(file)
        games.insert(0, game)
        
with open('C:\\DATA\\games.json', 'w') as file:
    json.dump(games, file)