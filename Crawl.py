from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup as bs
import os

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
    '''Parse the chapter result. Return the list of chapters in type of tuple (name,href).
    '''
    rtls=[]
    soup=bs(res.text,'html.parser')
    chapters=soup.find_all('a',class_='comics-chapters__item')
    for chapter in chapters:
        name=chapter.text
        href=chapter.attrs['href']
        single=(name,href)
        rtls.append(single)
    return rtls

def Parse_Pages(res:requests.Response):
    '''Parse the page result in one chapter. Return the list of page.
    '''
    rtls=[]
    soup=bs(res.text,'html.parser')
    sub=soup.find('ul',class_='comic-contain')
    pages=sub.find_all('amp-img')
    for page in pages:
        dir={}
        dir['width']=page.attrs['width']
        dir['height']=page.attrs['height']
        dir['src']=page.attrs['src']
        rtls.append(dir)
    return rtls

def Rename_Page(url):
    return url.split('scomic/')[-1].replace('/','_')

def Rename_Cover(url):
    return url.split('/')[-1]
    
def Cache(flag:int,url:str,path:str):
    '''Download the page. 可改进协程
    flag 1 for page, 0 for cover.
    '''
    down_res = requests.get(url)
    if flag==0:
        filename=Rename_Cover(url)
    elif flag==1:
        filename=Rename_Page(url)
    complete_path=path+filename
    if os.path.exists(complete_path)==False:
        with open(complete_path,'wb') as file:
            file.write(down_res.content)
    else:
        print('Already exist {}'.format(complete_path))

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
        chapter_res=Get_Response(Ses,rtls[0]['href'])
        chapter_list=Parse_Chapters(chapter_res)
        page_res=Get_Response(Ses,chapter_list[0][1])
        page_list=Parse_Pages(page_res)
        print(page_list)
        current_path = os.path.abspath(__file__)
        dirname=os.path.dirname(current_path)
        cache_path=dirname+'\\Cache\\'
        for page in page_list:
            Cache(1,page['src'],cache_path)


