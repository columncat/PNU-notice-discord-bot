import discord
from discord.ext import commands, tasks
from app_private import token
from app_private import mec_channel
from app_private import test_channel
import os.path
import csv
import time
from typing import List
import mec_notice
import mec_graduate
import mec_scholarship
import main_notice
import main_recruit
import main_scholar
import job_recruit
import main_schedule


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
QUEUE_FILE = "push_queue.csv"

alivetime = time.localtime()
localtime = time.localtime()
prev_time = localtime
show_debug = False


def time_to_str(time: time.struct_time) -> str:
    def int_to_str(num: int):
        return ('0' if num < 10 else '') + str(num)
    yr:str = str(time.tm_year)
    mon:str = int_to_str(time.tm_mon)
    day:str = int_to_str(time.tm_mday)
    hr:str = int_to_str(time.tm_hour if time.tm_hour <= 12 else time.tm_hour - 12)
    min:str = int_to_str(time.tm_min)
    ampm:str = 'AM' if time.tm_hour < 12 else 'PM'
    return f'{yr}-{mon}-{day} {hr}:{min} {ampm}'

def read_csv(path:str):
    content = []
    if not os.path.isfile(path):
        return content
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 3:
                content.append(row)
    return content

def update_all() -> int:
    count = 0
    count += mec_notice.update()
    count += mec_graduate.update()
    count += mec_scholarship.update()
    count += main_notice.update()
    count += main_recruit.update()
    count += main_scholar.update()
    count += job_recruit.update()
    count += main_schedule.update()
    return count


@tasks.loop(seconds=20)
async def check_updates():
    global prev_time, localtime, show_debug
    localtime = time.localtime()
    local_min = localtime.tm_min
    prev_min  = prev_time.tm_min
    
    if local_min % 5 == 0 and local_min != prev_min:
        prev_time = localtime
        count = update_all()
        if count > 0:
            updates = read_csv(QUEUE_FILE)
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
            await channel.send(f'{count} messages sent.')
        elif show_debug:
            channel = bot.get_channel(test_channel)
            await channel.send('no updates.')
    elif show_debug:
        channel = bot.get_channel(test_channel)
        await channel.send('waiting for interval.')

@bot.event
async def on_ready():
    check_updates.start()
    channel = bot.get_channel(test_channel)
    debug_status = 'on' if show_debug else 'off'
    await channel.send(f'started bot: {time_to_str(alivetime)}, debug: {debug_status}')


@bot.event
async def on_message(message):
    if message.channel.id == test_channel:
        channel = bot.get_channel(test_channel)
        if message.content.startswith('/help'):
            await channel.send(f'available commands are: /help, /debug, /hello, /whoami, /alive, /last_update, /bot_status, /shutdown')
        
        elif message.content.startswith('/debug'):
            global show_debug
            debug_args = message.content.split(' ')
            if len(debug_args) < 2:
                await channel.send('At least one argument is required for this operation.')
            elif debug_args[1] == 'on':
                show_debug = True
                await channel.send('debug mode: on')
            elif debug_args[1] == 'off':
                show_debug = False
                await channel.send('debug mode: off')
            else:
                await channel.send('invalid argument.')
        
        elif message.content.startswith('/hello'):
            user_id = str(message.author).split('#')[0]
            await channel.send(f'Hello {user_id}!')
        
        elif message.content.startswith('/whoami'):
            await channel.send(f'you are: {message.author}')
        
        elif message.content.startswith('/alive'):
            await channel.send(f'bot alive since: {time_to_str(alivetime)}')
        
        elif message.content.startswith('/last_update'):
            await channel.send(f'last update: {time_to_str(prev_time)}')
        
        elif message.content.startswith('/bot_status'):
            await channel.send(f'bot status: {bot.status}')
        
        elif message.content.startswith('/shutdown'):
            shutdown_args = message.content.split(' ')
            if len(shutdown_args) < 2:
                await channel.send('At least one argument is required for this operation.')
            elif shutdown_args[1] == 'now':
                await channel.send('shutdown: status_normal')
                bot.close()
                exit(0)
            elif shutdown_args[1] in ['init_err', 'trig_err', 'push_err']:
                await channel.send(f'shutdown: {shutdown_args[1]}')
                bot.close()
                exit(1)
            else:
                await channel.send('invalid argument.')


if __name__ == "__main__":
    bot.run(token)