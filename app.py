import time
import discord
from discord.ext import commands
from app_private import token
from app_private import mec_channel
from app_private import test_channel
import os.path
import csv
import mec_notice
import mec_graduate
import mec_scholarship
import main_notice
import main_recruit
import main_scholar
import job_recruit
import main_schedule
bot = commands.Bot(command_prefix='#', intents=discord.Intents.all())

QUEUE_FILE = "push_queue.csv"


def __read_csv(path):
    content = []
    if not os.path.isfile(path):
        return content
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 3:
                content.append(row)
    return content


def update_all():
    mec_notice.update()
    mec_graduate.update()
    mec_scholarship.update()
    main_notice.update()
    main_recruit.update()
    main_scholar.update()
    job_recruit.update()
    main_schedule.update()


@bot.event
async def on_ready():
    print(f'Login bot: {bot.user}')
    localtime = time.localtime().tm_min
    prev_time = localtime
    update_interval = 5
    try:
        channel = bot.get_channel(test_channel)
        await channel.send('initializing bot...')
        update_all()
        await channel.send('bot successfully initialized.')
        while True:
            # only trigger update every 5 minutes
            localtime = time.localtime().tm_min
            if localtime % update_interval == 0 and localtime != prev_time:
                prev_time = localtime
                
                # get updated
                update_all()
                updates = __read_csv(QUEUE_FILE)
                
                # send messages
                if updates:
                    for (id, title, url) in updates:
                        channel = bot.get_channel(int(id))
                        if (url != 'empty'):
                            embed = discord.Embed()
                            embed.description = f"[{title}]({url})"
                            if (int(id)) == mec_channel:
                                await channel.send(f"@everyone {title}", embed=embed)
                            else:
                                await channel.send(title, embed=embed)
                        else:
                            await channel.send(title)
                    
                    open(QUEUE_FILE, "w")   # flush queue
                    channel = bot.get_channel(test_channel)
                    await channel.send(f'{len(updates)} messages sent.')
            else:
                time.sleep(20)
    finally:
        channel = bot.get_channel(test_channel)
        await channel.send('@everyone bot shutting down due to internal error...')
        exit(1)


if __name__ == "__main__":
    bot.run(token)