import discord
from discord.ext import commands
from app_private import token
import os.path
import csv
import mec_notice
import main_notice
import main_recruit
import main_scholar
import main_schedule
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
    mec_notice.update()
    main_notice.update()
    main_recruit.update()
    main_scholar.update()
    main_schedule.update()


def push():
    updates = __read_csv(QUEUE_FILE)
    if updates.__len__() > 0:
        @bot.event
        async def on_ready():
            print(f'Login bot: {bot.user}')
            for (id, title, url) in updates:
                channel = bot.get_channel((int)(id))
                if (url != 'empty'):
                    embed = discord.Embed()
                    embed.description = f'[{title}]({url})'
                    await channel.send(embed=embed)
                else:
                    await channel.send(title)
            open(QUEUE_FILE, "w")
            exit()

        bot.run(token)


if __name__ == "__main__":
    update_all()
    push()
