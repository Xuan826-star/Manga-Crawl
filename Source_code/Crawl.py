from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup as bs

base='https://www.baozimh.com/'

def Get_Response(ses:requests.Session,href:str,**kwargs):
    '''Search based on the name. Return the response.

    'ses' is the session object.
    'href' is the sub under the base url.
    'kwargs' is the key words needed.
    
    '''
    try:
        res=ses.get(base+href,**kwargs)
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
def Parse_Chapters(res:requests.Response):
    '''Parse the chapter result. Yield the dict of chapter&href. 50 chapters per time. 
    '''
    pass

if __name__=='__main__':
    Name='我独自升级'
    param={'q':Name}
    shref='search'
    Ses=requests.session()
    rtv=Get_Response(Ses,shref,params=param)
    if rtv!=None:
        # print(rtv.text.find(Name))
        rtls=Parse_Search(rtv)
        # print(rtls)


