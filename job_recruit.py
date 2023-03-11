import requests
import os.path
from app_private import job_recruit_channel
from bs4 import BeautifulSoup


INDEX_FILE = "job_recruit.txt"
NOTICE_URL = "https://job.pusan.ac.kr/ko/recruit/board"
CHANNEL_ID = job_recruit_channel
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
    items = __get_soup(NOTICE_URL).select('li.tbody')
    updates = []
    for item in items:
        title = item.select_one(".subject").select_one("a").text.strip()
        link = NOTICE_URL[0:23] + \
            item.select_one(".subject").select_one("a").attrs["href"]
        num = (int)(link.split('/')[-1])
        if current < num:
            updates.append([title.replace("\"", "\'").replace(
                "[", "{").replace("]", "}"), link, num])
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
