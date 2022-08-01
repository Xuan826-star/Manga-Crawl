from distutils.log import info
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup as bs

base='https://www.baozimh.com/'

def Search(ses:requests.Session,name:str):
    '''Search based on the name. Return the response.

    'ses' is the session object.
    'name' is the target name.
    
    '''
    param={'q':name}
    try:
        res=ses.get(base+'search',params=param)
        res.raise_for_status()
        res.encoding='utf-8'
        return res
    except HTTPError:
        print('Request Fail')
        return None

def Parse_Search(res:requests.Response):
    '''Parse the search result. Return key info of each in a list of dic 
    '''
    rtls=[]
    soup=bs(res.text,'html.parser')
    # print(soup.prettify()[50000:60000])
    lst=soup.find_all('div',class_="comics-card pure-u-1-2 pure-u-sm-1-2 pure-u-md-1-4 pure-u-lg-1-6")
    for obj in lst:
        dic={}
        info1,info2=obj.find_all('a')
        dic['title']=info1.attrs['title']
        dic['href']=info1.attrs['href']
        dic['src']=info1.next.attrs['src']
        dic['author']=info2.find('small').text.strip()
        rtls.append(dic)
    return rtls

if __name__=='__main__':
    Name='我独自升级'
    Ses=requests.session()
    rtv=Search(Ses,Name)
    if rtv!=None:
        # print(rtv.text.find(Name))
        rtls=Parse_Search(rtv)
        print(rtls)

