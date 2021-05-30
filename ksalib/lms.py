import requests
from bs4 import BeautifulSoup
from datetime import datetime

from Auth import Auth
from simplefunctions import to_http, str_to_time

main_url = 'http://lms.ksa.hs.kr'
login_url = main_url + '/Source/Include/login_ok.php'
board_url = main_url + '/nboard.php?db=vod&scBCate={}'
post_url = main_url + '/nboard.php?db=vod&mode=view&idx={}&page=1&ss=on&sc=&sn=&db=vod&scBCate={}'

def get_lms_response(auth, link):
    link = to_http(link)
    if auth.lms_login is not None:
        cookies = {
            'PHPSESSID': auth.SESSION_ID
        }
        headers = {
            'Referer': login_url
        }
        # get html (site does not have XHR)
        response = requests.post(link, headers=headers, cookies=cookies)
    else:
        raise Exception('No LMS login')
    return response

class Comment:
    def __init__(self, author, content, time):
        self.author = author
        self.content = content
        self.time = time

    def __str__(self):
        return f'{self.author}: {self.content}'


class Post:
    def __init__(self, auth, index, scBCate):
        self.auth = auth
        self.index = index
        self.scBCate = scBCate
        self._get_info()

    def _get_info(self):
        link = post_url.format(self.index, self.scBCate)
        print(link)
        response = get_lms_response(self.auth, link)
        print(response.text)
        soup = BeautifulSoup(response.text,'html.parser')
        self.article = soup.find("div", {"id": "NBoardContetnArea"}).text
        self.title = soup.find("span", {"class": "title"}).text.strip()
        self.author = soup.find("span", {"class": "blue01"}).text.replace('\t','').replace(u'\xa0', u' ').strip()
        self.comments = []
        comments = soup.find('div', {'id': 'NBoardCommentArea'}).findChildren('table', recursive=False)
        for comment in comments:
            td = comment.find('td')
            author = td[0].text.strip()
            content = td[1].find(text=True)
            time = td[1].find('find').text.strip()
            time = str_to_time(time)
            self.comments.append(Comment(author, content, time))
