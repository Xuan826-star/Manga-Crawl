
from PySide2.QtWidgets import QApplication, QMessageBox,QLabel,QWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QRegularExpression
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
        self.result = Search(self.ses,reslist)
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

class Search:
    def __init__(self,session,reslist):
        self.ui = QUiLoader().load(dirname+'\GUI\search.ui')
        self.ses=session
        self.lst=reslist
        self.ui.search_button.clicked.connect(self.search)
        onelst=self.ui.findChildren(QWidget,one_re)
        onelen=len(onelst)
        for i in range(onelen):
            Crawl.Cache(0,reslist[i]['href'],cache_path)
            picname=Crawl.Rename_Cover(reslist[i]['href'])
            onelst[i].findChild(QLabel,'src_{}'.format(i+1)).setPixmap()

            
            

    def search(self):
        name=self.ui.search_text.text()
        param={'q':name}
        shref='search'
        rtv=Crawl.Get_Response(self.ses,shref,params=param)
        if rtv!=None:
            rtls=Crawl.Parse_Search(rtv)
            print(rtls)

    def open_result_window(self,reslist):
        # 实例化另外一个窗口
        self.result = Search(self.ses,reslist)
        # 显示新窗口
        self.result.ui.show()
        self.ui.close()

app = QApplication([])
ses=requests.session()
home_0 = Home(ses)
home_0.ui.show()
app.exec_()