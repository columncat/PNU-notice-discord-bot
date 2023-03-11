import requests
import os.path
from app_private import mec_scholarship_channel
from bs4 import BeautifulSoup


INDEX_FILE = "mec_scholarship.txt"
NOTICE_URL = "https://me.pusan.ac.kr/new/sub05/sub01_05.asp"
CHANNEL_ID = mec_scholarship_channel
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
    rows = __get_soup(NOTICE_URL).select('tbody>tr:not(.notice)')
    updates = []
    for row in rows:
        num = (int)(row.select_one("a").attrs["href"][20:-1])
        if current < num:
            updates.append(num)
    return updates


def __get_title(num):
    url = f'https://me.pusan.ac.kr/new/sub05/sub01_05.asp?seq={num.__str__()}&db=supervision&page=1&perPage=20&SearchPart=BD_SUBJECT&SearchStr=&page_mode=view'
    title = __get_soup(url).select_one(
        "div.board-view").select_one("dd").text.strip().replace('\"', '\'').replace("[", "{").replace("]", "}")
    return title


def update():
    fileContent = __read_file(INDEX_FILE)
    current = 0
    if fileContent.__len__() > 0:
        current = (int)(fileContent)
    updates = __check_notice(current)
    if (updates.__len__() > 0):
        queue = ""
        for update in updates:
            title = __get_title(update)
            url = f'https://me.pusan.ac.kr/new/sub05/sub01_05.asp?seq={update.__str__()}&db=supervision&page=1&perPage=20&SearchPart=BD_SUBJECT&SearchStr=&page_mode=view'
            queue += f'{CHANNEL_ID},"{title}", {url}\n'
        __write_file(QUEUE_FILE, "a", queue)
        __write_file(INDEX_FILE, "w", updates[0].__str__())


if __name__ == "__main__":
    update()
