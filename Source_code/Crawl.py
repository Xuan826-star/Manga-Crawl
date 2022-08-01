from sqlite3 import paramstyle
import string
from tokenize import String
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup as bs

base='https://www.baozimh.com/'

def Search(ses:requests.Session,name:string):
    '''Search based on the name.
    ses is the session object.
    '''
    param={'q':name}
    try:
        res=ses.get(base,params=param)
        res.raise_for_status()
        res.encoding='utf-8'
        return res
    except HTTPError:
        print('Request Fail')
        return None

Name='我独自升级'
Ses=requests.session()
rtv=Search(Ses,Name)
if rtv!=None:
    print(rtv.text.find(Name))
