# Manga-Crawl
本项目为针对漫画网站<a href="https://baozimh.org/">包子漫画</a>的网络爬虫以及UI。使用python编程主要基于requests和kivy库搭建。

<hr>

## 起因

当初找到该网站十分惊喜但使用期间的广告实在糟心，所以打算用python爬虫到自己的UI来避免广告。 最初是用pyqt5来设计的UI界面，使用后发现在电脑上看漫画不方便就暂时搁置了。最近使用ChatGPT快速掌握了kivy进而重新写了UI和爬虫编码（网站更新了）。 打算打包成apk放到手机上。


<hr>

## 项目细节

主要代码存放在Kivy文件夹下，qt版本的也留了但是没更新应该用不了。主要使用requests库对作品信息以及图片地址进行爬取然后用kivy的UI进行呈现（就是个图片的搬运工）。UI界面十分简陋但功能有了，反正自己用。

### 主要功能

<ul>
  <li>通过搜索功能来查找漫画</li> 
  <li>漫画采用下拉式，可根据窗口等比缩放</li> 
  <li>可记录浏览历史</li> 
  <li>可刷新的热门推荐</li> 
</ul>

### 存在问题

<ul>
  <li>热门推荐代码是个对热门页面爬取的生成器，不是真随机</li> 
  <li>漫画内容观看时应为Scrollview是底部作为0点，在异步加载中会产生抖动（图片本身大小与初始占位不不一样）</li> 
  <li>历史记录只到章节没到页数，所以不能快速跳转</li> 
  <li>UI过于简陋</li>
  <li>图片加载不会取消，导致快速切换章节时，图片加载过慢</li>
</ul>

<hr>

## 声明

本项目纯学习自用，任何商用行为概不负责。
