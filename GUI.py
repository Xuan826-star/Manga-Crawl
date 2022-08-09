from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
import requests
import os
import Crawl
current_path = os.path.abspath(__file__)
dirname=os.path.dirname(current_path)
print(dirname)
class home:
    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load(dirname+'\GUI\main.ui')
        self.ses=requests.session()
        self.ui.search_button.clicked.connect(self.search)

    def search(self):
        name=self.ui.search_text.text()
        param={'q':name}
        shref='search'
        rtv=Crawl.Get_Response(self.ses,shref,params=param)
        if rtv!=None:
            rtls=Crawl.Parse_Search(rtv)
            print(rtls)

app = QApplication([])
home_0 = home()
home_0.ui.show()
app.exec_()