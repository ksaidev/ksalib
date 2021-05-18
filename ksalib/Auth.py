import requests
import random
import string

# global SESSION_ID

# SESSION_ID=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

class Auth:
    def __init__(self, student_login=None, lms_login=None, gaonnuri_login=None, number=None, name=None):
        self.student_login = student_login
        self.lms_login = lms_login
        self.gaonnuri_login = gaonnuri_login
        self.number = number
        self.name = name
        self.SESSION_ID = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

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

    def student_auth(self,id,pwd):
        if 'main'in requests.post('http://students.ksa.hs.kr/scmanager/stuweb/loginProc.jsp',data={'id':str(id),'pwd':str(pwd)}).text:
            self.student_login={'id':id,'pwd':pwd}
            print('Login Succesful')
        else:
            print('Wrong Login')

    def lms_auth(self,id,pwd):
        if 'location.replace'in requests.post('http://lms.ksa.hs.kr/Source/Include/login_ok.php', data={'user_id': id,'user_pwd': pwd}).text:
            self.lms_login={'id':id,'pwd':pwd}
            print('Login Succesful')
        else:
            print('Wrong Login')

    def gaonnuri_auth(self,id,pwd):
        cookies = {
            'PHPSESSID': self.SESSION_ID
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
        response = requests.post('http://gaonnuri.ksain.net/xe/index.php', headers=headers, cookies=cookies, data=data)
        if 'window.opener' in response.text:
            self.gaonnuri_login={'id':str(id),'pwd':str(pwd)}
            print('Login Succesful')
        else:
            print('Wrong Login')    
