from kivy.properties import DictProperty,StringProperty, ObjectProperty, ListProperty, AliasProperty, BooleanProperty, NumericProperty, ColorProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image,AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from Crawl_V2 import *
from kivy.loader import Loader
from kivy.config import Config
from requests.adapters import HTTPAdapter
from datetime import datetime
import pandas as pd 
import os

Loader.max_upload_per_frame=8
Loader.num_workers = 8
Config.set('graphics', 'fullscreen', 'auto')
Window.size = (Window.width, Window.height)
header={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63',
        'referer': 'https://baozimh.org/',
        'cookie': '_ga=GA1.1.887496211.1679213885; __gads=ID=22d1ae889f90be94-229f551573dc006c:T=1679213885:RT=1679213885:S=ALNI_MYfeGfev6TpO5QCwx5zc7G7vyeDjw; __gpi=UID=00000bdbf5cbbc45:T=1679213885:RT=1679213885:S=ALNI_MbqzB7izDLavXfZFjmj_p4zdiobkA; _ga_KMWK3HTJJQ=GS1.1.1679213884.1.1.1679215263.0.0.0',
        }
nor_session=requests.sessions.Session()
nor_session.mount('http://', HTTPAdapter(max_retries=3))
nor_session.mount('https://', HTTPAdapter(max_retries=3))
nor_session.headers.update(header)

if not os.path.exists('history.csv'):
    print('history not exist')
    with open('history.csv','w') as f_obj:
        f_obj.write('title,src,href,chapter,time\n')
else:
    print('history exist')

history_ptr={}



class ArtworkContainer(BoxLayout):
    def __init__(self,parent_screen,artwork_item,**kwargs):
        super().__init__(**kwargs)
        self.parent_screen=parent_screen
        self.title=artwork_item.get('title')
        self.img=artwork_item.get('src')
        self.href=artwork_item.get('href')
        self.orientation = 'vertical'
        self.bind(minimum_height=self.setter('height'))
        # Create an image widget
        self.asyncimage = AsyncImage(source=self.img,keep_ratio=True,allow_stretch=True,size_hint=(1,1))
        # self.asyncimage.fbind('texture_size',self.asyncimage.setter('size'))

        
        # Create a label widget
        self.label = Label(text=self.title,size_hint_y=None,halign='center',height=20,shorten=True,shorten_from='right')
        self.label.fbind('size',self.label.setter('text_size'))

        # Add the image and label widgets to the container
        self.add_widget(self.asyncimage)
        self.add_widget(self.label)

    def update_size_from_height(self,*args):
        w=self.asyncimage.texture_size[0]*self.height/self.asyncimage.texture_size[1]
        self.asyncimage.size=(w,self.height)
        self.width=w
        print('new width:',w)
        print(self.asyncimage.size)
        print(self.size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button=='left':
                # The container was clicked
                print('Container clicked',self.title)
                self.perform_chapter()
                global history_ptr
                history_ptr={
                    'title':self.title,
                    'src':self.img,
                    'href':self.href,
                    'chapter':None,
                    'time':None
                    }
                return True
        return super().on_touch_down(touch)
        
    def perform_chapter(self):
        screenM : ScreenManager=self.parent_screen.m
        if 'chapter' not in screenM.screen_names:
            chapter_screen=ChapterScreen(m=screenM,artwork_name=self.title,url=self.href,name='chapter')
            screenM.add_widget(chapter_screen)
        else:
            sc : ChapterScreen = screenM.get_screen('chapter')
            sc.artwork_name=self.title
            sc.url=self.href
        screenM.current='chapter'

class ChapterButton(Button):
    def __init__(self, parent_screen,chapter_item,prevB=None,nextB=None,**kwargs):
        super().__init__(**kwargs)
        self.parent_screen=parent_screen
        self.href=chapter_item.get('href')
        self.text=chapter_item.get('name')
        self.on_press=self.perform_content
        self.prevB=prevB
        self.nextB=nextB
    
    def perform_content(self,*args):
        global history_ptr
        print(f'open {self.text} {self.href}')
        self.background_color=(0,0,1,1)
        screenM : ScreenManager=self.parent_screen.m
        if 'content' not in screenM.screen_names:
            print(self.prevB.text,self.nextB.text)
            chapter_screen=ContentScreen(m=screenM,chapter_name=self.text,
                                        url=self.href,
                                        prevB=self.prevB,nextB=self.nextB,
                                        name='content')
            screenM.add_widget(chapter_screen)
        else:
            sc : ContentScreen = screenM.get_screen('content')
            sc.chapter_name=self.text
            sc.url=self.href
            sc.prevB=self.prevB
            sc.nextB=self.nextB
        screenM.current='content'
        history_ptr['chapter']=self.text
        history_ptr['time']=datetime.now()
        home= screenM.get_screen('home')
        home.history_record_pd=home.history_record_pd.append(history_ptr,ignore_index=True)

class HomeScreen(Screen):
    history_record=ListProperty([])
    history_record_pd=ObjectProperty(None,force_dispatch=True)
    m=ObjectProperty(None,allownone=True)
    recommand_result=ListProperty([])
    recommand_generator=ObjectProperty(None)

    def update_recommand_result(self,*args):
        print('update recommand result')
        if not self.recommand_generator:
            raise Exception('None generator')
        self.recommand_result=next(self.recommand_generator)

    def update_history_record(self,*args):
        print('update history record')
        self.history_record_pd.drop_duplicates('title',keep='last',inplace=True)
        self.history_record=self.history_record_pd.to_dict('records')

    def update_history(self,*args):
        print('update history view')
        self.history_view_layout.clear_widgets()
        for record in self.history_record:
            temp=ArtworkContainer(self,record,size_hint_x=None)
            temp.asyncimage.bind(texture_size=temp.update_size_from_height)
            self.history_view_layout.add_widget(temp)

    def update_recommand(self,*args):
        print('update recommand view')
        self.recommand_layout.clear_widgets()
        # self.recommand_layout.rows=ceil(len(self.search_result)/2)
        for item in self.recommand_result:
            self.recommand_layout.add_widget(ArtworkContainer(self,item))
    
    def clear_history(self,*args):
        print('clear history')
        self.history_record_pd=self.history_record_pd.drop(index=self.history_record_pd.index)
        print(self.history_record_pd)
        
    def __init__(self,**kw):
        self.history_record_pd=pd.read_csv('history.csv')
        self.history_record_pd['time']=self.history_record_pd['time'].apply(pd.to_datetime)
        # Define the layout
        self.layout = BoxLayout(orientation='vertical')
        self.recommand_generator=Generate_Recommand(nor_session)
        # Create a label
        self.label = Label(text='Manga Reader',height=30)
        self.label.size_hint = (1, None)
        
        # Create a button to go to the search screen
        self.search_bar = TextInput(text='我独自升级',font_name="DroidSansFallback.ttf",size_hint_y=None,height=30)
        self.search_button = Button(text='search', on_press=self.perform_search,size_hint_y=None,height=30)
        
        self.scrolling_view=ScrollView(smooth_scroll_end=10)
        self.scrolling_view_layout=BoxLayout(orientation='vertical',size_hint_y=None)
        self.scrolling_view_layout.bind(minimum_height=self.scrolling_view_layout.setter('height'))
        
        self.history_label_box=BoxLayout(orientation='horizontal',height=30,size_hint_y=None)
        self.history_label=Label(text='历史记录',height=30,halign='left')
        self.history_button_clean=Button(text='清除记录',background_color=(0, 1, 0, 1),height=30,halign='right')
        self.history_button_clean.on_press=self.clear_history
        self.history_label_box.add_widget(self.history_label)
        self.history_label_box.add_widget(self.history_button_clean)

        self.fbind('history_record_pd',self.update_history_record)
        self.history_view=ScrollView(do_scroll=(True,False),size_hint_y=None,height=200,smooth_scroll_end=10)
        self.history_view_layout=BoxLayout(spacing=10,height=200,orientation='horizontal',size_hint=(None,None))
        self.history_view_layout.bind(minimum_width=self.history_view_layout.setter('width'))
        self.history_view.add_widget(self.history_view_layout)
        self.fbind('history_record',self.update_history)

        self.recommand_button=Button(text='换一换',height=30,halign='right',size_hint_y=None)
        self.recommand_button.on_press=self.update_recommand_result
        self.recommand_layout=GridLayout(cols=2,rows=3,spacing=10,size_hint_y=None,padding=(0,0))
        self.recommand_layout.row_default_height=200
        self.recommand_layout.bind(minimum_height=self.recommand_layout.setter('height'))

        self.fbind('recommand_result',self.update_recommand)
        self.scrolling_view_layout.add_widget(self.history_label_box)
        self.scrolling_view_layout.add_widget(self.history_view)
        self.scrolling_view_layout.add_widget(self.recommand_button)
        self.scrolling_view_layout.add_widget(self.recommand_layout)
        self.scrolling_view.add_widget(self.scrolling_view_layout)

        # Add the label and button to the layout
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.search_bar)
        self.layout.add_widget(self.search_button)
        self.layout.add_widget(self.scrolling_view)

        super().__init__(**kw)
        self.update_recommand_result()
        self.update_history_record()
        # Set the layout as the screen's content
        self.add_widget(self.layout)
        
    def perform_search(self,*args):
        search_name=self.search_bar._get_text()
        search_screen=SearchScreen(m=self.m,search_name=search_name,name='search')
        self.m.add_widget(search_screen)
        self.m.current='search'

class SearchScreen(Screen):
    search_name=StringProperty(None)
    url=StringProperty(base)
    search_result=ListProperty(None)
    m=ObjectProperty(None,allownone=True)

    def update_search_result(self,*args):
        if not self.search_name:
            print('None Search')
        search_response=nor_session.get(base,params={'s':self.search_name})
        self.search_result=Parse_Search_Page(search_response)

    def __init__(self,**kw):
        
        self.fbind('search_name',self.update_search_result)
        self.fbind('search_result',self.update_result)
        # self.search_name=search_name
        # self.search_result=search_result
    
        # Define the layout
        self.layout = BoxLayout(orientation='vertical')

        # Create a label
        self.label = Label(text=f'搜索结果:{self.search_name}',size_hint_y=None,height=30,halign='center')
        self.label.size_hint=(1,None)


        # Create a search bar and a search button
        self.search_bar = TextInput(size_hint_y=None,height=30)
        self.search_bar.size_hint=(1,None)

        self.search_button = Button(text='Search', size_hint_y=None,height=30,on_press=self.perform_search)
        self.search_button.size_hint=(1,None)


        self.search_view=ScrollView()
        self.result_layout=GridLayout(cols=2,spacing=10,size_hint_y=None,padding=(0,0))
        self.result_layout.row_default_height=200
        # self.update_result()
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.search_view.add_widget(self.result_layout)
        # Add the label, search bar, and search button to the layout
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.search_bar)
        self.layout.add_widget(self.search_button)
        self.layout.add_widget(self.search_view)
        
        super().__init__(**kw)
        # Set the layout as the screen's content
        self.add_widget(self.layout)
        

    def update_result(self,*args):
        self.search_bar.text=self.search_name
        self.label.text=f'搜索结果:{self.search_name}'
        self.result_layout.clear_widgets()
        # self.result_layout.rows=ceil(len(self.search_result)/2)
        for item in self.search_result:
            self.result_layout.add_widget(ArtworkContainer(self,item))
        self.search_view.scroll_y=1
    
    def perform_search(self,event):
        name=self.search_bar._get_text()
        self.search_name=name
        # search_response=nor_session.get(base,params={'s':name})
        # self.search_result=Parse_Search_Page(search_response)
        # self.update_result()

class ChapterScreen(Screen):
    artwork_name=StringProperty('')
    url=StringProperty(None)
    chapter_result=ListProperty(None)
    m=ObjectProperty(None,allownone=True)

    def update_label_text(self,*args):
        self.label.text=self.artwork_name

    def update_chapter_result(self,*args):
        if not self.url:
            print('None url')
        chapterList_url=self.url.replace('manga','chapterlist')
        chapterList_response=nor_session.get(chapterList_url)
        self.chapter_result=Parse_ChapterList_Page(chapterList_response)

    def __init__(self,**kw):
        self.fbind('artwork_name',self.update_label_text)
        self.fbind('url',self.update_chapter_result)
        self.fbind('chapter_result',self.update_result)
        # Define the layout
        self.layout = BoxLayout(orientation='vertical')

        self.navigator = BoxLayout(orientation='horizontal',size_hint_y=None,height=30)
        self.backbutton = Button(text='<---',on_press=self.back_screen,background_color=(1, 0, 0, 1))
        self.backbutton.size_hint_x=0.15
        # Create a label
        self.label = Label(text=self.artwork_name,height=50,text_size=(400, None),halign='center')
        self.label.size_hint=(1,None)
        
        self.reversebutton = Button(text='R',background_color=(0, 1, 0, 1),
                                    on_press=self.reverse_order)
        self.reversebutton.size_hint_x=0.15
        
        self.navigator.add_widget(self.backbutton)
        self.navigator.add_widget(self.label)
        self.navigator.add_widget(self.reversebutton)

        self.chapter_view=ScrollView()
        self.result_layout=GridLayout(cols=3,spacing=10,size_hint_y=None,padding=(0,0))
        self.result_layout.row_default_height=30
        # self.update_result()
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.chapter_view.add_widget(self.result_layout)
        
        # Add the label, chapter bar, and chapter button to the layout
        self.layout.add_widget(self.navigator)
        self.layout.add_widget(self.chapter_view)
        
        super().__init__(**kw)
        # Set the layout as the screen's content
        self.add_widget(self.layout)
    
    def reverse_order(self,*args):
        self.result_layout.children=list(reversed(self.result_layout.children))
    
    def back_screen(self,*args):
        self.m.current=self.m.previous()
    
    def update_result(self,*args):
        self.result_layout.clear_widgets()
        # self.result_layout.rows=ceil(len(self.chapter_result)/2)
        nxt=None
        blue_color=(0, 0, 1, 1)
        records=self.m.get_screen('home').history_record_pd['chapter'].to_list()
        print(records)
        for item in self.chapter_result:
            curr=ChapterButton(self,item,shorten=True,shorten_from='right')
            if item['name'] in records:
                print('one blue button')
                curr.background_color=blue_color
            curr.bind(size=curr.setter('text_size'))
            self.result_layout.add_widget(curr)
            if nxt:
                curr.nextB=nxt
                nxt.prevB=curr
            nxt=curr
        self.chapter_view.scroll_y=1

class ContentScreen(Screen):
    chapter_name=StringProperty('')
    url=StringProperty(None)
    content_result=ListProperty(None)
    m=ObjectProperty(None,allownone=True)
    prevB=ObjectProperty(None,allownone=True)
    nextB=ObjectProperty(None,allownone=True)

    def update_content_result(self,*args):
        content_response=nor_session.get(self.url)
        self.content_result=Parse_Content_Page(content_response)

    def update_label_text(self,*args):
        self.label.text=self.chapter_name

    def __init__(self, **kw):
        self.fbind('chapter_name',self.update_label_text)
        self.fbind('url',self.update_content_result)
        self.fbind('content_result',self.update_result)
        

        self.layout = BoxLayout(orientation='vertical')

        self.navigator = BoxLayout(orientation='horizontal',size_hint_y=None,height=30)
        self.backbutton = Button(text='<---',on_press=self.back_screen,background_color=(1, 0, 0, 1))
        self.backbutton.size_hint_x=0.15
        # Create a label
        self.label = Label(text=self.chapter_name,height=50,text_size=(400, None),halign='center')
        self.label.size_hint=(1,None)
        self.topbutton = Button(text='T',background_color=(0, 1, 0, 1),
                                    on_press=self.scroll_toTop)
        self.topbutton.size_hint_x=0.15
        self.navigator.add_widget(self.backbutton)
        self.navigator.add_widget(self.label)
        self.navigator.add_widget(self.topbutton)


        self.content_view=ScrollView(smooth_scroll_end=10)
        self.result_layout=BoxLayout(orientation='vertical',spacing=0,size_hint=(1,None),padding=(0,0))
        self.result_layout.fbind('minimum_height',self.result_layout.setter('height'))
        # self.result_layout.fbind('minimum_width',self.result_layout.setter('width'))

        self.content_view.add_widget(self.result_layout)

        self.director=BoxLayout(orientation='horizontal',spacing=0,size_hint_y=None,height=30)
        
        self.chaB=Button(text='章节目录',on_press=self.back_chapter_screen)
        self.previous_button=Button(text='上一章')
        self.fbind('prevB',self.updatePB)
        self.next_button=Button(text='下一章')
        self.fbind('nextB',self.updateNB)
        
        self.director.add_widget(self.previous_button)
        self.director.add_widget(self.chaB)
        self.director.add_widget(self.next_button)

        # Add the label, search bar, and search button to the layout
        self.layout.add_widget(self.navigator)
        self.layout.add_widget(self.content_view)
        self.layout.add_widget(self.director)

        super().__init__(**kw)
        # Set the layout as the screen's content
        self.add_widget(self.layout)
    
    def updatePB(self,*arg):
        print(self.prevB.text)
        self.previous_button.on_press=self.prevB.perform_content

    def updateNB(self,*arg):
        print(self.nextB.text)
        self.next_button.on_press=self.nextB.perform_content

    def back_chapter_screen(self,*arg):
        if 'chapter' not in self.m.screen_names:
            print('no chpater screen exist ')
        self.m.current='chapter'

    def back_screen(self,*args):
        self.m.current=self.m.previous()

    def scroll_toTop(self,*args):
        self.content_view.scroll_y=1

    def set_box_size(self,obj,value):
        # print('set')
        screen_width, screen_height = Window.size
        h=screen_width/value[0]*value[1]
        obj.height=h

    def update_box_size(self,obj,width):
        # print('update')
        h=width/obj.texture_size[0]*obj.texture_size[1]
        obj.height=h
        
    def update_result(self,*args):
        for child in self.result_layout.children:
            print('stop',child)
            
        self.result_layout.clear_widgets()
        for item in self.content_result:
            temp=AsyncImage(source=item['href'],size_hint=(1,None),keep_ratio=True,allow_stretch=True)
            self.result_layout.add_widget(temp)
            temp.bind(width=self.update_box_size)#待改进，
            temp.bind(texture_size=self.set_box_size)
        
        self.content_view.scroll_y=1

class MangaReader(App):
    def build(self):
        # screen_width, screen_height = Window.size
        # print(screen_width)
        # app_height = int(screen_width * (16/9))

        # # Set the size and position of the app window
        # Window.size = (screen_width/2, app_height/2)
        # Create a screen manager and add the home screen and search screen
        
        self.screen_manager = ScreenManager()
        
        home_screen = HomeScreen(m=self.screen_manager,name='home')
        self.screen_manager.add_widget(home_screen)
        print(self.screen_manager.screen_names)
        
        # Set the size hint for the root layout to maintain the 9:16 aspect ratio
        

        # Return the screen manager
        return self.screen_manager
    
    def on_stop(self):
        print('save history csv')
        home=self.screen_manager.get_screen('home')
        home.history_record_pd.to_csv('history.csv',encoding='utf-8',index=False)
        return super().on_stop()

if __name__ == '__main__':
    __version__='1.0.0'
    MangaReader().run()
