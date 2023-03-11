import requests
import os.path
from datetime import datetime as dt
from app_private import main_schedule_channel
from bs4 import BeautifulSoup


INDEX_FILE = "main_schedule.txt"
NOTICE_URL = "https://www.pusan.ac.kr/kor/CMS/Haksailjung/view.do?mCode=MN076"
CHANNEL_ID = main_schedule_channel
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
    items = __get_soup(NOTICE_URL).select_one('tbody').select('tr')
    today = dt.now().strftime('%Y.%m.%d')
    updates = []
    for item in items:
        head = item.select_one("th").text
        if head.startswith(today):
            detail = item.select_one("td").text
            if current == detail:
                return []
            updates.append([f'{head} : {detail}'.replace("\"", "\'").replace(
                "[", "{").replace("]", "}"), "empty", detail])
    return updates


def update():
    fileContent = __read_file(INDEX_FILE)
    current = ""
    if fileContent.__len__() > 0:
        current = fileContent
    updates = __check_notice(current)
    if (updates.__len__() > 0):
        queue = ""
        for (title, url, num) in updates:
            queue += f'{CHANNEL_ID},"{title}",{url}\n'
        __write_file(QUEUE_FILE, "a", queue)
        __write_file(INDEX_FILE, "w", updates[-1][2])


if __name__ == "__main__":
    update()
