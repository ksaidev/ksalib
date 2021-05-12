import requests
from bs4 import BeautifulSoup
from .parserlib import HTMLTableParser

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