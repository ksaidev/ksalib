import requests
from bs4 import BeautifulSoup

from .simplefunctions import to_http

main_url = 'http://www.ksa.hs.kr'

# does not support authorization
# help needed
def get_ksa_response(link):
    link = to_http(link)
    response = requests.get(link)
    return response

class Page:
    def __init__(self, link):
        self.link = link
        self._get_info()

    def _get_info(self):
        response = get_ksa_response(self.link)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', {'class':'page_content'})
        if content:
            self.content = content.text
        else:
            self.content = ''
        title = soup.find('h2', {'class':'page_title'})
        if title:
            self.title = title.text
        else:
            self.title = ''

# returns dict with link -> page name
# (example: 'https://www.ksa.hs.kr/Home/Sub/194' -> '학교장 인사말')
# excludes external sites, community(requires authentication)
def get_all_pages():
    response = get_ksa_response(main_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    menus = ['main-menu1', 'main-menu2', 'main-menu4', 'main-menu6', 'main-menu7']
    page_dict = {}
    for menu in menus:
        menu_li = soup.find('li', {'class':menu})
        ul = menu_li.findChildren('ul', recursive=False)[0]
        li = ul.findChildren('li', recursive=False)
        for l in li:
            a = l.findChildren('a', recursive=False)[0]
            page_dict[main_url+a['href']] = a.text.strip()
    return page_dict
