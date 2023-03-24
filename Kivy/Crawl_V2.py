from urllib.error import HTTPError
import requests
from lxml import etree


base='https://baozimh.org/'

def Get_Response(ses:requests.Session,href:str,**kwargs):
    '''Search based on the name. Return the response.

    'ses' is the session object.
    'href' is the sub under the base url.
    'kwargs' is the key words needed.
    
    '''
    try:
        res=ses.get(href,**kwargs)
        res.raise_for_status()
        res.encoding='utf-8'
        return res
    except HTTPError:
        print('Request Fail')
        return None

def Generate_Recommand(ses):
    response=Get_Response(ses,base+'hots/')
    root=etree.HTML(response.text)
    article_list=root.xpath('//article')[1:]
    result_list=[]
    idx=0
    while True:
        try:
            article=article_list[idx]
            idx+=1
        except:#Out of index, need new page.
            print('out of index ')
            idx=0
            tag=root.xpath('//a[@class="next page-numbers"]/@href')
            if not tag: #Stop the generator
                print('Reach the End')
                yield result_list
                break
            next_url=tag[0]
            print(next_url)
            response=Get_Response(ses,next_url)
            root=etree.HTML(response.text)
            article_list=root.xpath('//article')[1:]
        
        title=article.xpath('div/div/div//h2//text()')[0]
        href_selector=article.xpath('div/div/div//a')[0]
        href=href_selector.get('href')
        try:
            img_selector=href_selector.xpath('img')[0]
        except:
            img_selector={}
        src=img_selector.get('data-src',None)
        if src==None:
            continue
        item={
            'href':href,
            'title':title,
            'src':src,
        }
        result_list.append(item)
        if result_list.__len__()==6:
            yield result_list
            result_list.clear()


def Parse_Search_Page(response:requests.Response):
    root=etree.HTML(response.text)
    article_list=root.xpath('//article')
    result_list=[]
    for article in article_list:
        id=article.get('id')
        title=article.xpath('div/div/div//h2//text()')[0]
        href_selector=article.xpath('div/div/div//a')[0]
        href=href_selector.get('href')
        try:
            img_selector=href_selector.xpath('img')[0]
        except:
            img_selector={}
        src=img_selector.get('data-src',None)
        if src==None:
            continue
        item={
            'href':href,
            'title':title.strip(),
            'src':src,
        }
        # print(item)
        result_list.append(item)
    return result_list

def Parse_ChapterList_Page(response:requests.Response):
    root=etree.HTML(response.text)
    chapter_list=root.xpath('//*[@class="main version-chaps"]/a')
    # print(len(chapter_list))
    result_list=[]
    for chapter in chapter_list:
        href=chapter.get('href')
        name=chapter.text
        item={
            'name':name.strip(),
            'href':href,
        }
        # print(item)
        result_list.append(item)
    return result_list

def Parse_Content_Page(response:requests.Response):
    root=etree.HTML(response.text)
    content_list=root.xpath('//*[@id="main"]//img')
    result_list=[]
    for content in content_list:
        href=content.get('data-src')
        if not href:
            continue
        label=content.get('title')
        item={
            'name':label.strip(),
            'href':href,
        }
        # print(item)
        result_list.append(item)
    return result_list

if __name__=='__main__':
    
    # Name='我独自'
    # param={'s':Name}
    header={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63',
        'referer': 'https://baozimh.org/',
        'cookie': '_ga=GA1.1.887496211.1679213885; __gads=ID=22d1ae889f90be94-229f551573dc006c:T=1679213885:RT=1679213885:S=ALNI_MYfeGfev6TpO5QCwx5zc7G7vyeDjw; __gpi=UID=00000bdbf5cbbc45:T=1679213885:RT=1679213885:S=ALNI_MbqzB7izDLavXfZFjmj_p4zdiobkA; _ga_KMWK3HTJJQ=GS1.1.1679213884.1.1.1679215263.0.0.0',
        }
    # # aio_session=aiohttp.ClientSession()
    nor_session=requests.sessions.Session()
    nor_session.headers.update(header)
    # search_response=nor_session.get(base,params=param)
    # # print(search_response.url)
    # # print(search_response.text)
    # search_result=Parse_Search_Page(search_response)
    # selection=search_result[0]
    # chapterList_url=selection['href'].replace('manga','chapterlist')
    # chapterList_response=nor_session.get(chapterList_url)
    # chapterList_result=Parse_ChapterList_Page(chapterList_response)
    # content_url=chapterList_result[0]['href']
    # content_response=nor_session.get(content_url)
    # content_result=Parse_Content_Page(content_response)
    # # print(content_result)
    gen=Generate_Recommand(nor_session)
    for i in range(50):
        print(next(gen))


    