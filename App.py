from ast import Str
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import QPixmap,QFontMetrics
from functools import partial
import Crawl,os,requests,time
current_path = os.path.abspath(__file__)
dirname=os.path.dirname(current_path)
cache_path=dirname+'\\Cache\\'
ses=requests.session()

class ClickableLabel(QLabel):
    def __int__(self,href=None):
        super().__init__()
        self.sethref(href)
    
    def sethref(self,href):
        self.href=href

    def connect(self,func):
        self.clickfunc=func

    def mousePressEvent(self, QMouseEvent):  ##ClickEvent
        if QMouseEvent.buttons() == Qt.LeftButton:   ##Check it is left click
            print(self.href+'is clicked.')##What to do if left click
            self.clickfunc()
    
    def enterEvent(self, QMouseEvent):   ##Mouse Stay
        self.setToolTip(self.href)  ##Stay Hint

class BookFace(QWidget):
    def __init__(self,pare:QWidget,img:QPixmap,title:Str,author:Str,href:Str):
        super().__init__()
        self.pare=pare
        self.img=img
        self.title=title
        self.author=author
        self.href=href
        lo_V1=QVBoxLayout()
        #Fil the image, title, author
        bf_im=ClickableLabel()#image
        bf_im.connect(self.openhref)
        bf_im.sethref(href)
        bf_im.setPixmap(img)
        bf_im.setScaledContents(True)
        # bf_im.setBaseSize(110,150)
        bf_nm=ClickableLabel()#title
        bf_nm.connect(self.openhref)
        bf_nm.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        bf_nm.sethref(href)
        FontM=QFontMetrics(bf_nm.font())
        nm=FontM.elidedText(title,Qt.ElideRight,170)
        bf_nm.setText(nm)
        bf_au=QLabel()#author
        bf_au.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        bf_au.setText(author)
        lo_V1.addWidget(bf_im)
        lo_V1.addWidget(bf_nm)
        lo_V1.addWidget(bf_au)
        self.setLayout(lo_V1)
        # self.setMinimumSize(170,250)
    
    def openhref(self):
        rtv=Crawl.Get_Response(self.pare.ses,self.href)
        if rtv!=None:
            reslist=Crawl.Parse_Chapters(rtv)
            print(reslist)
            self.result = ChapterPage(self.pare,reslist)
            self.pare.hide()
            self.result.show()

class HomePage(QWidget):
    def __init__(self,session=ses):
        super().__init__()
        self.ses=session
        lo_all=QVBoxLayout()
        #Put the Search Part
        sc=self.CreateSearch()
        lo_all.addWidget(sc)
        #Combine all Parts
        self.setLayout(lo_all)
        self.setMinimumSize(750,1000)
        self.show()

    def CreateSearch(self):
        #Create the Search Part
        lo_H1=QHBoxLayout()
        sc_lb1=QLabel('Search')
        sc_tb1=QPlainTextEdit()
        sc_tb1.setPlaceholderText('Name')
        sc_pb1=QPushButton('Confirm')
        sc_pb1.clicked.connect(self.OpenResultPage)
        lo_H1.addWidget(sc_lb1)
        lo_H1.addWidget(sc_tb1)
        lo_H1.addWidget(sc_pb1)
        wg_sc=QWidget()
        wg_sc.setLayout(lo_H1)
        return wg_sc
    
    def OpenResultPage(self):
        #Open the Result Page Based on the Input Text
        tb=self.findChild(QPlainTextEdit)
        name=tb.toPlainText()
        param={'q':name}
        shref='search'
        rtv=Crawl.Get_Response(self.ses,shref,params=param)
        if rtv!=None:
            rtls=Crawl.Parse_Search(rtv)
            print(rtls)
            self.ResultPage=ResultPage(self,rtls)
            self.hide()
            self.ResultPage.show()

class ResultPage(QWidget):
    def __init__(self,pare,reslist,session=ses):
        super().__init__()
        self.pare=pare
        self.ses=session
        lo_Va=self.Create12Result(reslist[:12])
        self.setLayout(lo_Va)
        self.setMinimumSize(750,1000)

    def Create12Result(self,reslist12):
        #Generate 12 Result and return the layout
        lo_V1=QVBoxLayout()
        lo_H1=QHBoxLayout()
        j=0
        for res in reslist12:
            Crawl.Cache(0,res['src'],cache_path)
            picname=Crawl.Rename_Cover(res['src'])
            pixm=QPixmap(cache_path+picname).scaled(300,400,Qt.IgnoreAspectRatio)
            One=BookFace(self,pixm,res['title'],res['author'],res['href'])
            lo_H1.addWidget(One)
            j+=1
            if j%4==0:
                print('finish one row')
                lo_V1.addLayout(lo_H1)
                lo_H1=QHBoxLayout()
        return lo_V1
    
    def closeEvent(self,event):
        self.pare.show()
        event.accept()

class ChapterButton(QPushButton):
    def __init__(self,pare,name,thishref):
        super().__init__(text=name)
        self.this=thishref
        self.pare=pare
        self.clicked.connect(self.OpenPages)

    def SetNextb(self,nextb):
        self.nextb=nextb
    
    def SetPreb(self,preb):
        self.preb=preb

    def OpenPages(self):
        rtv=Crawl.Get_Response(ses,self.this)
        if rtv!=None:
            reslist=Crawl.Parse_Pages(rtv)
            print(reslist)
            self.result = Pages(self,reslist)
            self.pare.hide()
            self.result.show()


class ChapterPage(QWidget):
    def __init__(self, pare,reslist,session=ses):
        super().__init__()
        self.ses=session
        self.lst=reslist
        self.pare=pare
        rowlo=QHBoxLayout()
        collo=QVBoxLayout()
        scroll=QScrollArea()
        all=QWidget()
        all.setLayout(collo)
        count=0
        preb=None
        for i in reslist:
            if count==5:
                collo.addLayout(rowlo)
                rowlo=QHBoxLayout()
                count=0#rest the count
            pb=ChapterButton(self,i[0],i[-1])#Add the buttom here.
            pb.preb=preb
            if pb.preb!=None:
                pb.preb.nextb=pb
            pb.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
            pb.setFixedSize(170,30)
            pb.setStyleSheet('text-align:left')
            preb=pb
            rowlo.addWidget(pb)
            count+=1
        pb.nextb=None#The Last One doesn't have next button
        scroll.setMinimumSize(400,400)
        scroll.setWidget(all)
        Chaplo=QVBoxLayout()
        Chaplo.addWidget(scroll)
        self.setLayout(Chaplo)
        self.setMinimumSize(900,1000)

    def closeEvent(self,event):
        self.pare.show()
        event.accept()

class Pages(QWidget):
    def __init__(self,pare:ChapterButton,reslist,session=ses):
        super().__init__()
        self.ses=session
        self.lst=reslist
        self.pare=pare
        collo=QVBoxLayout()
        scroll=QScrollArea()
        all=QWidget()
        all.setLayout(collo)
        collo.setSpacing(0)
        for i in reslist:
            Crawl.Cache(1,i,cache_path)
            picname=Crawl.Rename_Page(i)
            pixm=QPixmap(cache_path+picname)
            lb=QLabel()
            lb.setPixmap(pixm)
            collo.addWidget(lb)
        scroll.setMinimumSize(750,400)
        scroll.setWidget(all)
        Pglo=QVBoxLayout()
        Pglo.addWidget(scroll)
        lo_bf=QHBoxLayout()
        bg_fb=QPushButton('Next')
        bg_bb=QPushButton('Previous')
        bg_mn=QPushButton('Chapters')
        bg_mn.clicked.connect(self.BacktoMeun)
        if self.pare.nextb!=None:
            bg_fb.clicked.connect(self.pare.nextb.OpenPages)
            bg_fb.clicked.connect(self.close)
        else:
            bg_fb.clicked.connect(self.PopNoneMessage)
        if self.pare.preb!=None:
            bg_bb.clicked.connect(self.pare.preb.OpenPages)
            bg_bb.clicked.connect(self.close)
        else:
            bg_bb.clicked.connect(self.PopNoneMessage)
        lo_bf.addWidget(bg_bb)
        lo_bf.addWidget(bg_mn)
        lo_bf.addWidget(bg_fb)
        wg_bf=QWidget()
        wg_bf.setLayout(lo_bf)
        Pglo.addWidget(wg_bf)
        self.setLayout(Pglo)
        self.setMinimumSize(750,1000)

    def PopNoneMessage(self):
        Mes=QMessageBox.warning(self,'Warning','There is no more chapter.')

    def BacktoMeun(self):
        self.pare.pare.show()
        self.close()

app = QApplication([])
home_0 = HomePage()
app.exec_()