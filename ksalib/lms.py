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
        with requests.Session() as s:
            s.post(login_url, data={'user_id': auth.lms_login['id'], 'user_pwd': auth.lms_login['pwd']})
            response = s.get(link)
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


post_labels = ['이름: ', '등록일: ', '최종수정일: ', '조회: ']

class Post:
    def __init__(self, auth, index, scBCate):
        self.auth = auth
        self.index = index
        self.scBCate = scBCate
        self._get_info()

    def _get_info(self):
        link = post_url.format(self.index, self.scBCate)
        response = get_lms_response(self.auth, link)
        soup = BeautifulSoup(response.text,'html.parser')
        self.article = soup.find("div", {"id": "NBoardContetnArea"}).text
        post_info = soup.find("span", {"class": "blue01"}).text.replace('\t','').replace(u'\xa0', u' ').strip()
        start = [post_info.find(label) for label in post_labels]
        info = [post_info[start[i]+len(post_labels[i]):start[i+1]] for i in range(len(post_labels)-1)]
        info.append(post_info[start[-1]+len(post_labels[-1]):])
        for i in range(len(info)):
            info[i] = info[i].strip()
        self.title = soup.find("span", {"class": "title"}).text.strip()
        self.author = info[0]
        self.time = str_to_time(info[1])
        self.last_edit = str_to_time(info[2])
        self.views = int(info[3])
        self.comments = []
        comments = soup.find('div', {'id': 'NBoardCommentArea'}).findChildren('table', recursive=False)
        for comment in comments:
            tr = comment.find('tr', {'class': 'Board'})
            td = tr.find_all('td')
            author = td[0].text.strip()
            content = td[1].find(text=True)
            time = td[1].find('font').text.strip()
            time = str_to_time(time)
            self.comments.append(Comment(author, content, time))

    def __str__(self):
        s = self.title
        s += '('
        s += f'{post_labels[0]}{self.author} '
        s += f'{post_labels[1]}{str(self.time)} '
        s += f'{post_labels[2]}{str(self.last_edit)} '
        s += f'{post_labels[3]}{str(self.views)}'
        s += ')'
        s += '\n' + self.article
        for c in self.comments:
            s += f'\n{c}'
        return s
