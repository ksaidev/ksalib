import requests
from bs4 import BeautifulSoup
import html2text
import random
import string
from .parserlib import HTMLTableParser
from .simplefunctions import download


global SESSION_ID

SESSION_ID=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

class Auth:

    def __init__(self, student_login=None, lms_login=None, gaonnuri_login=None, number=None, name=None):
        self.student_login = student_login
        self.lms_login = lms_login
        self.gaonnuri_login = gaonnuri_login
        self.number = number
        self.name = name

    def __str__(self):
        result={
            'login':{
                'student_login': self.student_login,
                'lms_login': self.lms_login,
                'gaonnuri_login' : self.gaonnuri_login
            },
            'info':{
                'name':self.name,
                'number':self.number
            }
        }
        return str(result)

    #student login

    def student_auth(self,id,pwd):
        if 'main'in requests.post('http://students.ksa.hs.kr/scmanager/stuweb/loginProc.jsp',data={'id':str(id),'pwd':str(pwd)}).text:
            self.student_login={'id':str(id),'pwd':str(pwd)}
            print('Login Succesful')
        else:
            print('Wrong Login')

    #LMS  login

    def lms_auth(self,id,pwd):
        if 'location.replace'in requests.post('http://lms.ksa.hs.kr/Source/Include/login_ok.php', data={'user_id': id,'user_pwd': pwd}).text:
            self.lms_login={'id':str(id),'pwd':str(pwd)}
            print('Login Succesful')
        else:
            print('Wrong Login')

    #gaonnuri login

    def gaonnuri_auth(self,id,pwd):

        cookies = {
            'PHPSESSID': SESSION_ID
        }

        headers = {
            'Referer': 'http://gaonnuri.ksain.net/xe/login'
        }

        data = {
        'user_id': id,
        'password': pwd,
        'act': 'procMemberLogin',
        'xeVirtualRequestMethod': 'xml'
        }

        response = requests.post('https://gaonnuri.ksain.net/xe/index.php', headers=headers, cookies=cookies, data=data)

        if 'window.opener' in response.text:
            self.gaonnuri_login={'id':str(id),'pwd':str(pwd)}
            print('Login Succesful')
        else:
            print('Wrong Login')    

####################### Gaonnuri ###############################

'''
음 가온누리에 뭔가를 올릴수 있는거를 만들까 싶은데 오작동하면 ㅈ되는거여서 고민되네
'''
#A class definig a single post
class Post:
    def __init__(self,Auth,link):
        self.link=link
        self.Auth=Auth

        if self.Auth.gaonnuri_login != None:

            cookies = {
                'PHPSESSID': SESSION_ID
            }

            headers = {
                'Referer': 'http://gaonnuri.ksain.net/xe/login'
            }

            #get html (site does not have XHR)
            responce = requests.post(self.link, headers=headers, cookies=cookies)
                
        else:
            raise Exception('No gaonnuri login')

        soup=BeautifulSoup(responce.text,'html.parser')


        article = soup.find('article')

        self.rare=article

        info = soup.find('div', {"class": "board clear"})

        #title
        title=info.find("h1")

        if title==None:
            pass
        else:
            title=title.text
            if title==None:
                pass
            else:
                title=title.strip()
        
        self.title=title

        #time
        time=info.find("div",{"class": "fr"})

        if time==None:
            pass
        else:
            time=time.text
            if time==None:
                pass
            else:
                time=time.strip()
        
        self.time=time     

        #author
        author=info.find("div",{"class":"side"})

        if author==None:
            pass
        else:
            author=author.text
            if author==None:
                pass
            else:
                author=author.strip()
        
        self.author=author

        #views
        views=info.find("div",{"class":"side fr"})

        if views==None:
            pass
        else:
            views=views.text
            if views==None:
                pass
            else:
                views=views.strip()
        
        self.views=views

    def __str__(self):
        return str(self.rare)

    def html(self):
        return str(self.rare)
    
    def text(self):
        h = html2text.HTML2Text()
        return h.handle(str(self.rare))

#returns list of Post classes
def get_gaonnuri_board_post(Auth,board="board_notice"):

    if Auth.gaonnuri_login != None:

        link='http://gaonnuri.ksain.net/xe/'+board


        cookies = {
            'PHPSESSID': SESSION_ID
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

            #link
            title=x.find("td",class_="title")

            title_link=title.find("a")

            if title_link==None:
                link=None
            else:
                try:
                    link=title_link['href']
                    post=Post(Auth,link)
                    list_posts.append(post)
                except:
                    pass

        return list_posts
            
    else:
        raise Exception('No gaonnuri login')

#returns only basic information
def get_gaonnuri_board(Auth,board="board_notice"):

    if Auth.gaonnuri_login != None:

        link='http://gaonnuri.ksain.net/xe/'+board


        cookies = {
            'PHPSESSID': SESSION_ID
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

            if no==None:
                pass
            else:
                no=no.text
                if no==None:
                    pass
                else:
                    no=no.strip()  

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
                    title

            if title_link==None:
                link=None
            else:
                try:
                    link=title_link['href']
                except:
                    pass




            #author
            author=x.find("td",class_="cate")
            

            if author==None:
                author=x.find("td",class_="author")
            
            if author==None:
                pass
            else:
                author=author.text

            #time
            time=x.find("td",class_="time")

            if time==None:
                pass
            else:
                time=time.text
            
            #views
            views=x.find("td",class_="m_no")

            if views==None:
                pass
            else:
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
            'PHPSESSID': SESSION_ID
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

############################### Student #################################

class Sugang:
    def __init__(self,Auth):
        self.Auth=Auth
        with requests.Session() as s:
            response = s.post('http://students.ksa.hs.kr/scmanager/stuweb/loginProc.jsp',  data={'id': self.Auth.student_login['id'],'pwd': self.Auth.student_login['pwd']})
            response = s.get('http://students.ksa.hs.kr/scmanager/stuweb/kor/sukang/state.jsp')
            self.html=response.text
    
    def table(self):
        soup=BeautifulSoup(self.html,'html.parser')

        table = soup.find("table", {"class": "board_list"})

        from parserlib import HTMLTableParser

        p = HTMLTableParser()
        p.feed(str(table))
        return p.tables
    
    def timetable(self):
        soup=BeautifulSoup(self.html,'html.parser')

        table = soup.find("table", {"class": "board_view","cellpadding":"1"})

        p = HTMLTableParser()
        p.feed(str(table))
        return p.tables
    
    def info(self):
        soup=BeautifulSoup(self.html,'html.parser')

        table = soup.find("table", {"class": "board_view","cellpadding":"0"})

        if table == None:
            raise Exception('Hmmm. You are probably not a member of KSA yet. The site does not seem to contain information about you')

        p = HTMLTableParser()
        p.feed(str(table))
        lst=p.tables
        lst=lst[0][0]+lst[0][1]
        try:
            lst = ({lst[0]:lst[1],lst[2]:lst[3],lst[4]:lst[5],lst[6]:lst[7],lst[8]:lst[9],lst[10]:lst[11]})
            return lst
        except IndexError:
            raise Exception("If you see this error, Please contact me on github")

def get_student_points(Auth):
    
    with requests.Session() as s:
        response = s.post('http://students.ksa.hs.kr/scmanager/stuweb/loginProc.jsp',  data={'id': Auth.student_login['id'],'pwd': Auth.student_login['pwd']})
        response = s.get('http://students.ksa.hs.kr/scmanager/stuweb/kor/life/rewardSearch_total.jsp')
        html=response.text

        soup=BeautifulSoup(html,'html.parser')

        table = soup.find("table", {"class": "board_list"})

        from parserlib import HTMLTableParser

        p = HTMLTableParser()
        p.feed(str(table))

        table = p.tables

        table=table[0]

        result={}

        for i in range(1,len(table)):
            dic={}
            for j in range(1,len(table[1])):
                dic[table[0][j]]=table[i][j]
            result[int(table[i][0])]=dic
        return result

####################### LMS ###############################

# Consider helping out! I don't have any ideas

####################### Exploits ###############################

# methods that are not supposed to be possible.
class Exploit:
    def __init__(self,Auth):

        self.Auth=Auth
    
    def outing(self):
        if self.Auth.number==None:
            raise Exception("Please provide a number to Auth by doing Auth().number")
        else:
            cookies = {
                'JSESSIONID': 'oooooooooooooooooooooo',
            }

            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Origin': 'http://sas.ksa.hs.kr',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Referer': 'http://sas.ksa.hs.kr/scmanager/outing/index.jsp',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            data = {
            'p_proc': 'regist',
            'in_out_yn': '1',
            'sch_no': self.Auth.number,
            '__encrypted': 'ppRpv5sAQLtvrDkcSoaqtr^%^2FafJazlNruuIKGoyK5yDbGHIk01KcHY8^%^2BeON8gMRB0k31KM6UgB^%^2BOgSBS7V6enb^%^2F4PIOHwBHZq'
            }

            response = requests.post('http://sas.ksa.hs.kr/scmanager/outing/proc.jsp', headers=headers, cookies=cookies, data=data, verify=False)

            if '존재하지 않습니다.' in response.text:
                print('Your number does not exist on the approved outing list.')
                return False
            else:
                print("It probably worked, but I'm not 100% sure, so check it yourself if you can")
                return True
        
    def lmsview(self,number):

        if self.Auth.lms_login==None:
            raise Exception('No lms login')

        link="http://lms.ksa.hs.kr/nboard.php?db=vod&mode=view&idx=%i&page=1&ss=on&sc=&sn=&db=vod&scBCate=447"%number


        with requests.Session() as s:
            response = s.post('http://lms.ksa.hs.kr/Source/Include/login_ok.php', data={'user_id': self.Auth.lms_login['id'],'user_pwd': self.Auth.lms_login['pwd']})
            response = s.get(link)
        
        soup=BeautifulSoup(response.text,'html.parser')

        article = soup.find("div", {"id": "NBoardContetnArea"})

        if article != None:
            h = html2text.HTML2Text()
            article = h.handle(str(article))

        title = soup.find("span", {"class": "title"}).text

        author = soup.find("span", {"class": "blue01"}).text.replace('\t','').replace(u'\xa0', u' ')

        return {'title':title,'author':author,'article':article}

    def lmsfile(self,number,path=''):

        if self.Auth.lms_login==None:
            raise Exception('No lms login')

        link="http://lms.ksa.hs.kr/NBoard/download.php?db=vod&idx=%i&fnum="%number

        counter=0

        for i in range(100):
            try:
                download(link+str(i),path)
            except:
                if counter>=2:
                    break
                counter+=1
