import requests
from bs4 import BeautifulSoup
import html2text
from .simplefunctions import try_find
from xml.dom.minidom import parseString
####################### Gaonnuri ###############################

#A class definig a single post

class Post:

    def __init__(self,Auth,link):
        self.link = link
        self.Auth = Auth
        self.comments = None

    def _get_rare(self):

        if self.Auth.gaonnuri_login != None:

            cookies = {
                'PHPSESSID': self.Auth.SESSION_ID
            }

            headers = {
                'Referer': 'http://gaonnuri.ksain.net/xe/login'
            }

            #get html (site does not have XHR)
            responce = requests.post(self.link, headers=headers, cookies=cookies)
            
        else:
            raise Exception('No gaonnuri login')

        soup = BeautifulSoup(responce.text,'html.parser')

        article = soup.find('article')

        self.rare = article

        info = soup.find('div', {"class": "board clear "})

        if info != None:

            #title
            title = info.find("h1")

            if title != None:
                title=title.text
                if title != None:
                    title=title.strip()
            
            self.title = title

            #time
            time=info.find("div",{"class": "fr"})

            self.time = try_find(time)

            #author
            author=info.find("div",{"class":"side"})

            self.author = try_find(author)

            #views
            views=info.find("div",{"class":"side fr"})

            self.views = try_find(views)

        comments = {}
        
        comment_soup = soup.find("ul",{"class":"fdb_lst_ul "})

        if comment_soup == None:
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
                comments[num] = {"name":c,"content":cmt}
            
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

        response = requests.post('http://gaonnuri.ksain.net/xe/index.php', headers=headers, cookies=cookies, data=data.encode('utf-8'))

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

        response = requests.post('http://gaonnuri.ksain.net/xe/index.php', headers=headers, cookies=cookies, data=data.encode('utf-8'))

        response = parseString(response.text)

        response = response.getElementsByTagName('message')

        return f"{response[0].firstChild.nodeValue}"


    def __str__(self):
        self._get_rare()
        h = html2text.HTML2Text()
        return h.handle(str(self.rare))

    def html(self):
        self._get_rare()
        return str(self.rare)
    
    def text(self):
        self._get_rare()
        h = html2text.HTML2Text()
        return h.handle(str(self.rare))
    
    def comment(self):
        self._get_rare()
        return self.comments

    

class Board():
    def __init__(self, Auth, link):
        self.Auth = Auth
        self.link = link
    
    def posts(self):

        if self.Auth.gaonnuri_login != None:

            cookies = {
                'PHPSESSID': self.Auth.SESSION_ID
            }

            headers = {
                'Referer': 'http://gaonnuri.ksain.net/xe/login'
            }

            list_posts=[]

            #get html (site does not have XHR)
            responce = requests.post(self.link, headers=headers, cookies=cookies)
            soup=BeautifulSoup(responce.text,'html.parser')
            posts = soup.find_all('tr')

            #get rid of unneccesary elements in grid
            posts=posts[2:]

        else:
            raise Exception('No gaonnuri login')

        for x in posts:
            #link
            title=x.find("td",class_="title")

            title_link=title.find("a")

            if title_link==None:
                link=None

            else:
                try:
                    link = title_link['href']
                    post = Post(self.Auth,link)
                    list_posts.append(post)
                except:
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

        response = requests.post('http://gaonnuri.ksain.net/xe/index.php', headers=headers, cookies=cookies, data=data.encode('utf-8'))

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

        response = requests.post('http://gaonnuri.ksain.net/xe/index.php', headers=headers, cookies=cookies, data=data)

        response = parseString(response.text)

        response = response.getElementsByTagName('message')

        return response[0].firstChild.nodeValue

################################## extra useful functions #########################################

#returns only basic information
def get_gaonnuri_board(Auth,board="board_notice"):

    if Auth.gaonnuri_login != None:

        link='http://gaonnuri.ksain.net/xe/'+board


        cookies = {
            'PHPSESSID': Auth.SESSION_ID
        }

        headers = {
            'Referer': 'http://gaonnuri.ksain.net/xe/login'
        }

        list_posts=[]

        #get html (site does not have XHR)
        responce = requests.post(link, headers=headers, cookies=cookies)
        soup=BeautifulSoup(responce.text,'html.parser')
        posts = soup.find_all('tr')

        #get rid of unneccesary elements in grid
        posts=posts[2:]

        for x in posts:

            #number
            no=x.find("td",class_="no")

            no = try_find(no)

            #title, link
            title=x.find("td",class_="title")

            title_link=title.find("a")

            if title_link==None:
                title=None
            else:
                title=title_link.text
                if title==None:
                    pass
                else:
                    title=title.strip()

            if title_link==None:
                link=None
            else:
                try:
                    link=title_link['href']
                except:
                    pass

            #author
            author = x.find("td",class_="cate")
            

            if author == None:
                author = x.find("td",class_="author")
            
            if author != None:
                author=author.text

            #time
            time=x.find("td",class_="time")

            if time != None:
                time=time.text
            
            #views
            views=x.find("td",class_="m_no")

            if views != None:
                views=views.text

            #append info into list_posts
            info={
                'no':no,
                'title':title,
                'link':link,
                'author':author,
                'time':time,
                'views':views
            }

            list_posts.append(info)

        return list_posts
    
    else:
        raise Exception('No gaonnuri login')

#For oneline posts
def get_gaonnuri_oneline(Auth):

    if Auth.gaonnuri_login != None:

        link='http://gaonnuri.ksain.net/xe/index.php?mid=special_online'

        cookies = {
            'PHPSESSID': Auth.SESSION_ID
        }

        headers = {
            'Referer': 'http://gaonnuri.ksain.net/xe/login'
        }

        list_posts=[]


        #get html (site does not have XHR)
        responce = requests.post(link, headers=headers, cookies=cookies)
        soup=BeautifulSoup(responce.text,'html.parser')

        posts = soup.find_all("font",class_="xe_content")

        for x in posts:
            list_posts.append(x.text)
        
        return list_posts

    else:
        raise Exception('No gaonnuri login')