# 两个队列,一个队列抓取,一个队列解析,都使用多线程操作

import requests
from lxml import etree
import threading
from multiprocessing import Queue



class Crawl_thread(threading.Thread):  #继承于threading.Thread这个类
#     抓取线程
    def __init__(self,thread_id,pageQueue):
        threading.Thread.__init__(self)
        self.thread_id=thread_id
        self.pageQueue=pageQueue

    def run(self):
        print("启动了线程{}".format(self.thread_id))
        self.crawl_spider()
        print("退出了线程{}".format(self.thread_id))

    def crawl_spider(self):
        while True:
            if self.pageQueue.empty(): #判断队列是否为空
                break
            else:
                page=self.pageQueue.get() #获取队列里面的元素
                print('当前正在工作的线程是:{},正在采集第{}个页面'.format(self.thread_id,str(page)))
                url='https://www.qiushibaike.com/8hr/page/{}/'.format(str(page))
                headers={"User-Agent":'Mozilla5.0/'}
                try:
                    content=requests.get(url,headers=headers)
                    # content.encoding='utf-8'
                    data_queue.put(content.text)  #将网页源代码放入队列
                except Exception as e:
                    print('线程采集网页信息失败,错误信息:'+e)

class Parser_thread(threading.Thread):
#     解析线程
    def __init__(self,thread_id,data_queue,file):
        threading.Thread.__init__(self)
        self.thread_id=thread_id
        self.data_queue=data_queue
        self.file=file

    def run(self):
        print("启动了线程{}".format(self.thread_id))
        while not flag:
            try:
                item=self.data_queue.get(False)   #get取值时,队列为空就会抛出异常,所以需要用try
                # print(item)
                if not item:
                    pass
                self.parse_data(item)   #调用具体的解析函数
                # self.data_queue.task_done()  #每当get一次之后,提示是否阻塞
            except Exception as e:
                pass
        print("退出了线程{}".format(self.thread_id))

    def parse_data(self,item):
#         解析网页内容的函数
        try:
            html=etree.HTML(item)
            # print(html)
            result=html.xpath('//div[@class="content"]/span')
            for x in result:
                # print(x.text)
                a=x.text.strip()
                self.file.write(a+'\n')
            self.file.write('\n------------------------------------------------------\n\n')
        except:
            pass

data_queue=Queue() #创建一个队列
flag=False

# 主函数进行调用
def main():
    file=open('糗事百科1.txt','a',encoding='utf-8')
    pageQueue=Queue(50)
    for page in range(1,11):  #假设先爬取10页的url
        pageQueue.put(page)

    #初始化采集线程
    crawl_threads=[]
    crawl_name_list=['crawl_1','crawl_2','crawl_3']
    for thread_id in crawl_name_list:
        thread=Crawl_thread(thread_id,pageQueue)
        thread.start()
        crawl_threads.append(thread)
    #初始化解析线程
    parser_threads=[]
    parser_thread_list=['parser_1','parser_2','parser_3']
    for thread_id in parser_thread_list:
        thread=Parser_thread(thread_id,data_queue,file)
        thread.start()
        parser_threads.append(thread)
    # 等待抓取线程队列,如果不为空则继续
    while not pageQueue.empty():
        pass
    else:
        # 等待所有的线程结束
        for t in crawl_threads:
            t.join()

    # 等待解析的线程队列,如果不为空则继续
    while not data_queue.empty():
        pass
    else:
        #通知线程退出
        global flag
        flag=True
        for t in parser_threads:
            t.join()
        print('退出主线程')

    file.close()

if __name__=="__main__":
    main()



















