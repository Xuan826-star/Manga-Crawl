from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import *
from PySide2.QtGui import QPixmap,QFontMetrics
from functools import partial
import requests
import os
import Crawl

one_re=QRegularExpression()
one_re.setPattern('one.*')
current_path = os.path.abspath(__file__)
dirname=os.path.dirname(current_path)
cache_path=dirname+'\\Cache\\'
print(dirname)
class Home:
    def __init__(self,session):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load(dirname+'\GUI\main.ui')
        self.ses=session
        self.ui.search_button.clicked.connect(self.search)
    
    def open_result_window(self,reslist):
        # 实例化另外一个窗口
        self.result = Search(self.ses,reslist,self)
        # 显示新窗口
        self.result.ui.show()
        self.ui.hide()

    def search(self):
        name=self.ui.search_text.text()
        param={'q':name}
        shref='search'
        rtv=Crawl.Get_Response(self.ses,shref,params=param)
        if rtv!=None:
            rtls=Crawl.Parse_Search(rtv)
            print(rtls)
            self.open_result_window(rtls)

    def clean_cache(self):
        pass


class Search(Home):
    def __init__(self,session,reslist,parent):
        self.ses=session
        self.lst=reslist
        self.pare=parent
        self.ui = QUiLoader().load(dirname+'\GUI\search.ui')
        self.ui.search_button.clicked.connect(self.search)
        onelst=self.ui.findChildren(QWidget,one_re)
        onelen=len(onelst)
        for i in range(onelen):
            Crawl.Cache(0,reslist[i]['src'],cache_path)
            picname=Crawl.Rename_Cover(reslist[i]['src'])
            pixm=QPixmap(cache_path+picname).scaled(170,225)
            each_cover=onelst[i].findChild(QLabel,'src_{}'.format(i+1))
            each_cover.setPixmap(pixm)
            each_name=onelst[i].findChild(QPushButton,'name_{}'.format(i+1))
            FontM=QFontMetrics(each_name.font())
            name_text=FontM.elidedText(reslist[i]['title'],Qt.ElideRight,170)#prevent long string that elongate the widget
            each_name.setText(name_text)
            hf=reslist[i]['href']
            each_name.clicked.connect(partial(self.chapter,hf))
            each_author=onelst[i].findChild(QLabel,'author_{}'.format(i+1))
            each_author.setText(reslist[i]['author'])

    def chapter(self,href):
        print('clicked')
        print(href)
        rtv=Crawl.Get_Response(self.ses,href)
        if rtv!=None:
            reslist=Crawl.Parse_Chapters(rtv)
            print(reslist)
            self.result = Chapter(self.ses,reslist,self)
            self.ui.hide()
    
    def closeEvent(self,event):
        self.pare.ui.show()
        print('home page show again')
        event.accept()

class Chapter(QWidget):
    def __init__(self,session,reslist,parent):
        super().__init__()
        self.ses=session
        self.lst=reslist
        self.pare=parent
        rowlo=QHBoxLayout()
        collo=QVBoxLayout()
        scroll=QScrollArea()
        all=QWidget()
        all.setLayout(collo)
        count=0
        for i in reslist:
            if count==5:
                collo.addLayout(rowlo)
                rowlo=QHBoxLayout()
                count=0#rest the count
            pb=QPushButton(i[0])#Add the buttom here.
            pb.clicked.connect(partial(self.page,i[1]))
            pb.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
            pb.setFixedSize(120,30)
            pb.setStyleSheet('text-align:left')
            rowlo.addWidget(pb)
            count+=1
        scroll.setMinimumSize(400,400)
        scroll.setWidget(all)
        Chaplo=QVBoxLayout()
        Chaplo.addWidget(scroll)
        self.setLayout(Chaplo)
        self.setMinimumSize(700,1000)
        self.show()

    def page(self,href):
        rtv=Crawl.Get_Response(self.ses,href,self)
        if rtv!=None:
            reslist=Crawl.Parse_Pages(rtv)
            print(reslist)
            self.result = Page(self.ses,reslist)
            self.ui.hide()
    
    def closeEvent(self,event):
        self.pare.ui.show()
        event.accept()

class Page(QWidget):
    def __init__(self,session,reslist,parent):
        super().__init__()
        self.ses=session
        self.lst=reslist
        self.pare=parent
        collo=QVBoxLayout()
        scroll=QScrollArea()
        all=QWidget()
        all.setLayout(collo)
        collo.setSpacing(0)
        for i in reslist:
            Crawl.Cache(1,i['src'],cache_path)
            picname=Crawl.Rename_Page(i['src'])
            pixm=QPixmap(cache_path+picname)
            lb=QLabel()
            lb.setPixmap(pixm)
            collo.addWidget(lb)
        scroll.setMinimumSize(750,400)
        scroll.setWidget(all)
        Pglo=QVBoxLayout()
        Pglo.addWidget(scroll)
        self.setLayout(Pglo)
        self.setMinimumSize(750,1000)
        self.show()

    def closeEvent(self,event):
        self.pare.ui.show()
        event.accept()


app = QApplication([])
ses=requests.session()
home_0 = Home(ses)
home_0.ui.show()
app.exec_()