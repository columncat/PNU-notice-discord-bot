# pip install yfinance, tabulate
import requests
import os.path
from app_private import eec_channel
from bs4 import BeautifulSoup


INDEX_FILE = "eec_recent.txt"
NOTICE_URL = "https://eec.pusan.ac.kr/bbs/eehome/2650/rssList.do?row=50"
CHANNEL_ID = eec_channel
QUEUE_FILE = "push_queue.csv"


def __write_file(path, method, content):
    with open(path, method) as file:
        file.write(content)


def __read_file(path):
    if not os.path.isfile(path):
        return ""
    content = ""
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            content += line + "\n"
    return content[0:-1]


def __get_soup(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup


def __check_notice(current):
    global NOTICE_URL
    items = __get_soup(NOTICE_URL).select('item')
    updates = []
    for item in items:
        title = item.select_one("title").next_element
        link = item.select_one("link").next_element
        num = (int)(link.split('/')[-2])
        if current < num:
            updates.append([title.replace("\"", "\'"), link, num])
    return updates


def update():
    fileContent = __read_file(INDEX_FILE)
    current = 0
    if fileContent.__len__() > 0:
        current = (int)(fileContent)
    updates = __check_notice(current)
    if (updates.__len__() > 0):
        queue = ""
        for (title, url, num) in updates:
            queue += f'{CHANNEL_ID},"{title}",{url}\n'
        __write_file(QUEUE_FILE, "a", queue)
        __write_file(INDEX_FILE, "w", updates[0][2].__str__())


if __name__ == "__main__":
    update()
