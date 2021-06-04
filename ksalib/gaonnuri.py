import requests
from bs4 import BeautifulSoup
import html2text
from .simplefunctions import try_find, to_http, str_to_time
from xml.dom.minidom import parseString
from datetime import datetime
from collections import OrderedDict

gaonnuri_url = 'http://gaonnuri.ksain.net'
main_url = f'{gaonnuri_url}/xe/'
login_url = f'{main_url}login'
index_url = f'{main_url}index.php'
board_url = main_url + '{}'


def get_gaonnuri_response(Auth, link):
    link = to_http(link)
    if Auth.gaonnuri_login is not None:
        cookies = {
            'PHPSESSID': Auth.SESSION_ID
        }
        headers = {
            'Referer': login_url
        }
        # get html (site does not have XHR)
        response = requests.post(link, headers=headers, cookies=cookies)
    else:
        raise Exception('No gaonnuri login')
    return response

class Comment:
    def __init__(self,author,content,id):
        self.author = author
        self.content = content
        self.id = id

    def __str__(self):
        return f'{self.author}:{self.content}'


# A class defining a single post
class Post:
    def __init__(self,Auth,link):
        self.link = link
        self.Auth = Auth
        response = get_gaonnuri_response(self.Auth, self.link)
        self.soup = BeautifulSoup(response.text,'html.parser')
        self._get_rare()

    # get all basic information on post
    def _get_rare(self):
        soup = self.soup
        article = soup.find('article')
        self.rare = article
        info = soup.find('div', {"class": "board clear"})
        if info is not None:
            title = info.find("h1")
            if title is not None:
                title=title.text
                if title is not None:
                    title=title.strip()
            self.title = title
            time=info.find("div",{"class": "fr"})
            time = try_find(time)
            self.time = str_to_time(time, d1='.')
            author=info.find("div",{"class":"side"})
            self.author = try_find(author)
            others=info.find("div",{"class":"side fr"})
            others = others.text.split(' ')
            others = list(filter(lambda x: x.isdigit(), others))
            self.views = int(others[0])
        rec_button = soup.find('div', {'class':'rd_vote'})
        rec_button = rec_button.find_all('b')
        rec_button = list(filter(lambda x: x.text != '', rec_button))
        self.recommend = int(rec_button[0].text)
        self.unrecommend = -int(rec_button[1].text)
        comments = []
        comment_soup = soup.find("ul",{"class":"fdb_lst_ul"})
        if comment_soup is None:
            # print("no comments or fatal error")
            pass
        else:
            for x in comment_soup:
                try:
                    num = x["id"].split("_")[-1]
                except:
                    continue
                a = x.find_all("div")
                for b in a:
                    if "comment_" in b["class"][0]:
                        cmt = b.text
                        break

                c = x.find("div",{"class":"meta"})
                c = c.find("a")
                c = c.text
                comments.append(Comment(c, cmt, num))
        self.comments = comments

    def write_comment(self,content):
        cookies = {
            'PHPSESSID': self.Auth.SESSION_ID
        }
        headers = {
            'Referer': self.link
        }
        data = f'''<?xml version="1.0" encoding="utf-8" ?>
        <methodCall>
        <params>
        <_filter>insert_comment</_filter>
        <error_return_url>/xe/board_free/</error_return_url>
        <mid>{self.link.split("/")[-2]}</mid>
        <document_srl>{self.link.split("/")[-1]}</document_srl>
        <content>{content}</content>
        <use_html>Y</use_html>
        <module>board</module>
        <act>procBoardInsertComment</act>
        </params>
        </methodCall>'''
        response = requests.post(index_url, headers=headers, cookies=cookies, data=data.encode('utf-8'))
        response = parseString(response.text)
        response = response.getElementsByTagName('comment_srl')
        return f"{response[0].firstChild.nodeValue}"
    
    def delete_comment(self,number):
        cookies = {
            'PHPSESSID': self.Auth.SESSION_ID
        }
        headers = {
            'Referer': self.link
        }
        data = f'''<?xml version="1.0" encoding="utf-8" ?>
        <methodCall>
        <params>
        <_filter>delete_comment</_filter>
        <error_return_url>/xe</error_return_url>
        <act>procBoardDeleteComment</act>
        <mid>board_free</mid>
        <document_srl>{self.link.split("/")[-1]}</document_srl>
        <comment_srl>{number}</comment_srl>
        <module>board</module>
        </params>
        </methodCall>'''
        response = requests.post(index_url, headers=headers, cookies=cookies, data=data.encode('utf-8'))
        response = parseString(response.text)
        response = response.getElementsByTagName('message')
        return f"{response[0].firstChild.nodeValue}"

    def __str__(self):
        h = html2text.HTML2Text()
        return h.handle(str(self.rare))

    def html(self):
        return str(self.rare)
    
    def text(self):
        h = html2text.HTML2Text()
        return h.handle(str(self.rare))
    
    def comment(self):
        return self.comments


class Board:
    # board_name is not a link, it's the text that comes at the end of the link
    # example: board_notice, board_select
    def __init__(self, Auth, board_name):
        self.Auth = Auth
        self.board_name = board_name
        self.link = board_url.format(board_name)
        response = get_gaonnuri_response(self.Auth, self.link)
        soup=BeautifulSoup(response.text,'html.parser')
        self.first_page = soup

    # number of pages(not posts) on the board
    def page_num(self):
        soup = self.first_page
        try:
            if len(soup.find_all('strong', {'class':'direction'})) == 2:
                return 1
            else:
                last_page = soup.find('a', {'title':'끝 페이지'})
                return int(last_page.text)
        except ValueError:
            print('cannot find page number')

    # link to nth page of the board
    def page_link(self, page):
        return f'{index_url}?mid={self.board_name}&page={page}'

    # get all links of posts on the board
    def all_links(self):
        page_num = self.page_num()
        links = set()
        for page in range(1, page_num+1):
            links.update(self.links_in_page(page))
        return list(links)

    # get all links on a page of the board
    def links_in_page(self, page):
        link = self.page_link(page)
        response = get_gaonnuri_response(self.Auth, link)
        list_posts = []
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find_all('tr')
        # get rid of unnecessary elements in grid
        posts = posts[2:]
        for x in posts:
            try:
                title=x.find("td",class_="title")
                title_link=title.find("a")
                if title_link is not None:
                    link = title_link['href']
                    list_posts.append(link)
            except AttributeError:
                pass
        return list_posts

    def write_post(self,title,content):
        cookies = {
            'PHPSESSID': self.Auth.SESSION_ID
        }
        headers = {
            'Referer': self.link + '&act=dispBoardWrite',
        }
        data = f'''<?xml version="1.0" encoding="utf-8" ?>
        <methodCall>
        <params>
        <_filter>insert</_filter>
        <error_return_url>/xe/index.php?mid={self.link.split("/")[-1]}&amp;act=dispBoardWrite</error_return_url>
        <act>procBoardInsertDocument</act>
        <mid>{self.link.split("/")[-1]}</mid>
        <content>{content}
        </content>
        <document_srl>0</document_srl>
        <title>{title}</title>
        <comment_status>ALLOW</comment_status>
        <allow_trackback>Y</allow_trackback>
        <status>PUBLIC</status>
        <module>board</module>
        </params>
        </methodCall>'''
        response = requests.post(index_url, headers=headers, cookies=cookies, data=data.encode('utf-8'))
        response = parseString(response.text)
        response = response.getElementsByTagName('document_srl')
        return Post(self.Auth, f"{self.link}/{response[0].firstChild.nodeValue}")

    def delete_post(self,post_link):
        srl = post_link.split("/")[-1]
        cookies = {
            'PHPSESSID': self.Auth.SESSION_ID
        }
        headers = {
            'Referer': self.link + 'dispBoardDelete',
        }
        data = f'''<?xml version="1.0" encoding="utf-8" ?>
        <methodCall>
        <params>
        <_filter>delete_document</_filter>
        <error_return_url>/xe/index.php?mid={self.link.split("/")[-1]}&amp;document_srl={srl}&amp;act=dispBoardDelete</error_return_url>
        <act>procBoardDeleteDocument</act>
        <mid>{self.link.split("/")[-1]}</mid>
        <document_srl>{srl}</document_srl>
        <module>board</module>
        </params>
        </methodCall>'''
        response = requests.post(index_url, headers=headers, cookies=cookies, data=data)
        response = parseString(response.text)
        response = response.getElementsByTagName('message')
        return response[0].firstChild.nodeValue

################################## extra useful functions #########################################

# returns only basic information
def get_gaonnuri_board(Auth,board="board_notice"):
    link=board_url.format(board)
    response = get_gaonnuri_response(Auth, link)
    list_posts=[]
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('tr')
    # get rid of unnecessary elements in grid
    posts = posts[2:]
    for x in posts:
        # number
        no = x.find("td", class_="no")
        no = try_find(no)
        # title, link
        title = x.find("td", class_="title")
        title_link = title.find("a")
        if title_link is None:
            title = None
        else:
            title = title_link.text
            if title is None:
                pass
            else:
                title = title.strip()
        if title_link is None:
            link = None
        else:
            try:
                link = title_link['href']
            except:
                pass
        author = x.find("td", class_="cate")
        if author is None:
            author = x.find("td", class_="author")
        if author is not None:
            author = author.text
        time = x.find("td", class_="time")
        if time is not None:
            time = time.text
        views = x.find("td", class_="m_no")
        if views is not None:
            views = views.text
        # append info into list_posts
        info = {
            'no': no,
            'title': title,
            'link': link,
            'author': author,
            'time': time,
            'views': views
        }
        list_posts.append(info)
    return list_posts

#For one-line posts
def get_gaonnuri_oneline(Auth):
    link=f'{index_url}?mid=special_online'
    response = get_gaonnuri_response(Auth, link)
    list_posts = []
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all("font", class_="xe_content")
    for x in posts:
        list_posts.append(x.text)
    return list_posts

# returns dict with board_name -> board_label
# (example: 'board_notice' -> '공지사항')
def get_board_names(Auth):
    response = get_gaonnuri_response(Auth, main_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    dropdowns = soup.find_all('ul', {'class':'total_sub1'})
    boards = dropdowns[0]
    anchors = boards.find_all('a')
    names = OrderedDict()
    for a in anchors:
        link = a['href']
        start = link.rfind('/')+1
        names[link[start:]] = a.text.strip()
    return names

def get_special_links(Auth):
    response = get_gaonnuri_response(Auth, main_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    dropdowns = soup.find_all('ul', {'class': 'total_sub1'})
    boards = dropdowns[1]
    anchors = boards.find_all('a')
    links = []
    for a in anchors:
        links.append(a['href'])
    return links
