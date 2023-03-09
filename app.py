import discord
from discord.ext import commands
from app_private import token
import os.path
import csv
import eec_notice as eec
import mec_notice as mec
bot = commands.Bot(command_prefix='#', intents=discord.Intents.all())

QUEUE_FILE = "push_queue.csv"


def __read_csv(path):
    if not os.path.isfile(path):
        return []
    content = []
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row.__len__() == 3:
                content.append(row)
    return content


def update_all():
    mec.update()
    eec.update()


def push():
    updates = __read_csv(QUEUE_FILE)
    if updates.__len__() > 0:
        @bot.event
        async def on_ready():
            print(f'Login bot: {bot.user}')
            for (id, title, url) in updates:
                channel = bot.get_channel((int)(id))
                embed = discord.Embed()
                embed.description = f'[{title}]({url})'
                await channel.send(embed=embed)
            open(QUEUE_FILE, "w")
            exit()

        bot.run(token)


if __name__ == "__main__":
    update_all()
    push()
