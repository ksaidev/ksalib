import requests
from bs4 import BeautifulSoup
from urllib import parse
from collections import OrderedDict

from .simplefunctions import to_http, str_to_time

main_url = 'http://lms.ksa.hs.kr'
login_url = main_url + '/Source/Include/login_ok.php'
comm_url = main_url + '/Source/Community/vodBoard.php'
board_url = main_url + '/nboard.php?db=vod&scBCate={}'
board_page_url = main_url + '/nboard.php?page={}&ss=on&sc=&sn=&db=vod&scBCate={}'
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


class File:
    def __init__(self, link, name):
        self.link = link
        self.name = name

    def __str__(self):
        return self.name


post_labels = ['이름: ', '등록일: ', '최종수정일: ', '조회: ']

class Post:
    # enter link, or index and scBCate
    def __init__(self, auth, link=None, index=None, scBCate=None):
        self.auth = auth
        if link:
            self.link = link
            params = dict(parse.parse_qsl(parse.urlsplit(self.link).query))
            self.index = params.get('idx')
            self.scBCate = params.get('scBCate')
        else:
            self.index = index
            self.scBCate = scBCate
            self.link = post_url.format(index, scBCate)
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
        files = soup.find_all('a', {'class': 'Board2'})
        self.files = []
        for file in files:
            name = file.text.strip()
            name = name[:name.rfind('(')]
            self.files.append(File(main_url+file['href'], name))
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
        s += '\n'
        for f in self.files:
            s += f'{f} '
        s += '\n' + self.article
        for c in self.comments:
            s += f'\n{c}'
        return s


class Board:
    def __init__(self, auth, scBCate):
        self.auth = auth
        self.scBCate = scBCate
        self._get_info()

    def _get_info(self):
        link = board_url.format(self.scBCate)
        response = get_lms_response(self.auth, link)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('div', {'id': 'vodBoardTitle'}).text
        title = title.split('>')
        self.subject = title[0].strip()
        self.teacher = title[1].strip()
        boards = soup.find('div', {'id': 'vodBoardLeft'})
        self.name = boards.find('a', {'class': 'selected'}).text
        info = soup.find(class_='NB_tPageArea').text
        start = info.index(':') + 1
        end = info.index('건')
        self.post_num = int(info[start:end])
        start = info.index('/') + 1
        end = info.index('page')
        self.page_num = int(info[start:end])

    def __str__(self):
        return f'{self.subject} > {self.teacher} > {self.name}'

    def page_link(self, page):
        return board_page_url.format(page, self.scBCate)

    def get_links_page(self, page):
        link = self.page_link(page)
        response = get_lms_response(self.auth, link)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find('table', {'id': 'NB_ListTable'})
        tds = posts.find_all('td', {'class': 'tdPad4L6px'})
        links = []
        for td in tds:
            a = td.find('a')
            if a:
                links.append(main_url+a['href'])
        return links

    def get_all_link(self):
        links = set()
        for page in range(1, self.page_num+1):
            links.update(self.get_link_page(page))
        return list(links)

# returns dict with scBCate -> board name
# (example: 1563 -> '자료구조 선생님 자료실')
def get_all_boards(auth):
    response = get_lms_response(auth, comm_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    boards = soup.find('div', {'id': 'tutorListLayer'})
    nums = boards.find_all('a')
    boards = OrderedDict()
    for a in nums:
        if a.has_attr('vsidx'):
            boards[int(a['vsidx'])] = a.text.strip()
    return boards
