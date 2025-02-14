import json
from pprint import pp
import discord

class MatchmakingView(discord.ui.View):
    def __init__(self, queue):
        super().__init__(timeout=None)
        self.queue = queue

    @discord.ui.button(label="Matchmaking...", style=discord.ButtonStyle.gray, emoji="<a:loadingbuffering:949327277311803522>", disabled=True)
    async def matchmaking_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Leave queue", style = discord.ButtonStyle.red)
    async def leavequeue_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('C:\\DATA\\unlq.json', 'r') as file:
            unlq = json.load(file)
        if str(interaction.user.id) in unlq['in_queue'].keys():
            del unlq['in_queue'][str(interaction.user.id)]
            with open('C:\\DATA\\unlq.json', 'w') as unlq_file:
                json.dump(unlq, unlq_file)
        if self.queue.locked != True:
            list = self.queue.players
            for player in list:
                if interaction.user.id == player.user.id:
                    print(player.name + " left the queue")
                    self.queue.players.remove(player)
                    await self.queue.update_lobby()
                    await interaction.response.edit_message(content='You left the queue.', view=None)