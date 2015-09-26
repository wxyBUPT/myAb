#coding=utf-8
'''
产生负载压力的模块
'''
__author__ = 'xiyuanbupt'
import urllib
from aRequest import ARequset
from abLog import logger
class Pressurer(object):
    def __init__(self,url,userCount=1,visitCount=1,visitTime=None,userAgent=None,
                 outhString=None,cookie=None,method='GET',postData=None,protocal='http',
                 proxy=None):
        '''
        初始化压力请求信息
        :param url: 请求的url
        :param userCount: 模拟的用户数量
        :param visitCount: 总共的请求数量
        :param visitTime: 完成请求的时间
        :param userAgent: 代理浏览器
        :param outhString: 采用base64 向服务器提供的身份信息，注意是没有进行编码的信息
        :param cookie: 访问的cookie
        :param method: 请求方法，默认是GET
        :param postData: 如果请求方法是POST 则为经过编码的POST数据
        :param protocal: 使用协议，默认是Http协议
        :param proxy:
        :return:
        '''
        self.url=self.createURL(url,protocal)
        self.curlHeader=self.createHeaderForCurl(userAgent=userAgent,outhString=outhString,cookie=cookie)
        self.postData=self.createBodyForCurl(postData)
        self.method=method
        self.proxy=proxy
        self.userCount=userCount
        self.visitCount=visitCount

    def createURL(self,url,protocal='Http'):
        #返回格式类似https://www.baidu.com
        return "%s://%s"%(protocal,url)

    def createHeaderForCurl(self,userAgent=None,outhString=None,cookie=None,):
        '''
        创建请求头
        :param userAgent:
        :param outhString:
        :param cookie:
        :return:
        '''
        header=[]
        if userAgent is not None:
            tmp='User-Agent: %s'%userAgent
            header.append(tmp)
        if outhString is not None:
            import base64
            outhString=base64.b64encode(outhString)
            tmp='Authorization : Basic %s'%outhString
            header.append(tmp)
        if cookie is not None:
            tmp='Cookie:%s'%cookie
            header.append(tmp)
        return header

    def createBodyForCurl(self,postDate):
        '''
        确保包含postDate为字符串格式
        :param postDate:
        :return:
        '''
        if type(postDate)==type({}):
            return urllib.urlencode(postDate)
        elif type(postDate)==type(''):
            return postDate
        else:
            return ''

    def oneUserVisit(self,count):
        '''
        模拟一个用户访问count次
        :param count: 访问的次数
        :return:
        '''
        infoList=[]
        #logger.debug(u'方法:%s 地址:%s http头:%s 提交的数据:%s 代理%s'%(self.method,self.url,self.curlHeader,self.postData,self.proxy))
        for i in range(count):
            aRequest=ARequset(self.method,self.url,self.curlHeader,self.postData,self.proxy)
            tmpDict=aRequest.getABParDic()
            infoList.append(tmpDict)
        #logger.info(infoList)
        return infoList

    def userVisit(self,userCount,count):
        '''
        模拟userCount个用户同时访问共count次
        为每一个用户起一个线程
        :param userCount:
        :param count:
        :return:
        '''
        import threading
        infoList=[{}]*userCount
        threads=[]
        loops=range(userCount)

        def strategy(userCount,count):
            '''
            提供访问策略，返回数组
            :param userCount:
            :param count:
            :return:
            '''
            reArray=[0]*userCount
            import random
            for i in range(count):
                x=random.randint(0,userCount-1)
                reArray[x]+=1
            return reArray
        def usedByThread(userIndex,count):
            '''
            被线程调用的函数，与infoList共同解决了数据同步的问题
            :param userIndex: 代表第几个用户
            :param count: 代表这个用户访问了多少次
            :return:
            '''
            infoList[userIndex]=self.oneUserVisit(count)
            logger.info(u'第%d个用户访问的结果是%s'%((userIndex+1),infoList[userIndex]))
        stra=strategy(userCount,count)
        logger.info(u'%d个用户访问%d次，对应访问次数是%s'%(userCount,count,stra))
        for i in loops:
            t=threading.Thread(target=usedByThread,args=(i,stra[i],))
            threads.append(t)
        for i in loops:
            threads[i].start()
        for i in loops:
            threads[i].join()
        return infoList

    def getAveInfo(self,userCount,count):
        '''
        获得userCount个用户访问count的平均性能及各个指标
        :param userCount:
        :param count:
        :return:
        '''
        infoList=self.userVisit(userCount,count)
        logger.debug(u'过滤后在这里能够获得的信息有%s'%infoList)
        info={}
        info['totalRequest']=0
        info['messageCount']=0
        info['successCount']=0
        info['redirectCount']=0
        info['errorCount']=0
        info['serverErrCount']=0
        info['noHeaderCount']=0
        info['HTML transferred']=[]
        info['Document Length']=[]
        info['Waiting']=[]
        info['Name lookup time']=[]
        info['Total transferred']=[]
        info['Time taken for tests(not Run Time)']=[]
        info['Connect']=[]
        info['Server Software']=None
        info['Document Path']=None
        info['Server Hostname']=None
        info['Server IP']=None
        info['Server Port']=None
        #第一次对infoList遍历获得所有请求固定的内容
        def addCount(visitDict):
            '''
            增加对应的访问次数
            :param visitDict: 本函数中的一次访问情况的字典,规定同一个访问字典只可以访问一次
            :return:
            '''
            info['totalRequest']+=1
            httpStatusCode=visitDict['Http_code']
            code=httpStatusCode/100
            if code==1:
                info['messageCount']+=1
            elif code==2:
                info['successCount']+=1
            elif code==3:
                info['redirectCount']+=1
            elif code==4:
                info['errorCount']+=1
            elif code==5:
                info['serverErrCount']+=1
            else:
                info['noHeaderCount']+=1

        def addTimeAndSize(visitDict):
            '''
            增加有关每次访问的时间和传输内容长度的信息
            :param visitDict:
            :return:
            '''
            def addInfo(parList):
                '''
                添加添加属性的偷懒函数
                :param parList:
                :return:
                '''
                for par in parList:
                    info[par].append(visitDict[par])
            parList=['HTML transferred','Document Length','Waiting','Name lookup time','Total transferred','Connect']
            addInfo(parList)
            info['Time taken for tests(not Run Time)'].append(visitDict['Time taken for tests'])

        def insureHasValue(attris,info,userVist):
            '''
            给下面的for循环使用，用来保证相应的值只赋值一遍
            :param attris:属性列表
            :return:
            '''
            for attri in attris:
                if info[attri] is None:
                    info[attri]=userVist.get(attri,None)
                else:
                    continue

        for userVists in infoList:
            for userVist in userVists:
                attris=['Server Software','Document Path','Server Hostname','Server IP','Server Port']
                insureHasValue(attris,info,userVist)
        for userVists in infoList:
            for userVist in userVists:
                #logger.debug(u'每次访问的信息包含%s'%userVist)
                addCount(userVist)
                addTimeAndSize(userVist)
        return info

    def getShowFormat(self,userCount,count):
        aveInfo=self.getAveInfo(userCount,count)
        retDict={}
        retDict['Server Software']=aveInfo.get('Server Software','None')
        retDict['Server Hostname']=aveInfo.get('Server Hostname','None')
        retDict['Sever Port']=aveInfo.get('Server Port','None')
        retDict['Document Path']=aveInfo.get('Document Path','None')
        retDict['Document Length']='%d bytes'%(sum(aveInfo.get('Document Length',[])))
        timeTakenForTests=max(aveInfo.get('Time taken for tests(not Run Time)',[]))
        retDict['Time taken for tests']='%.6f seconds'%(timeTakenForTests)
        retDict['total requests']=aveInfo.get('totalRequest','error')
        retDict['200 requests']=aveInfo.get('successCount','error')
        retDict['100 requests']=aveInfo.get('messageCount','error')
        retDict['300 requests']=aveInfo.get('redirectCount','error')
        retDict['400 requests']=aveInfo.get('errorCount','error')
        retDict['500 requests']=aveInfo.get('serverErrCount','error')
        retDict['600 requests']=aveInfo.get('noHeaderCount','error')
        totalTransferred=sum(aveInfo.get('Total transferred',[]))
        retDict['Total transferred']='%.3f bytes'%(totalTransferred)
        retDict['HTML transferred']='%.3f bytes'%(sum(aveInfo.get('HTML transferred',[])))
        retDict['Requests per second']='%.3f [#/sec]'%(retDict['total requests']/timeTakenForTests)
        retDict['Time per request']='%.3f [ms]'%(1000*timeTakenForTests/retDict['total requests'])
        retDict['Transfer rate']='%.3f [Kbytes/sec]'%((totalTransferred/1024)/timeTakenForTests)
        aboutTimes={}
        aboutTimes['item']=['min','mean','median','max']
        def tmpCalc(retDictKey,renameKey):
            '''
            函数根据retDict中的对应项计算
            :param retDictKey:在retDict中的key值
            :param renameKey:充命名为
            :return:
            '''
            iArray=[0.0]*4
            source=aveInfo.get(retDictKey,[])
            iArray[0]=int(1000*min(source))
            iArray[1]=int(1000*(sum(source)/len(source)))
            iArray[2]=int(1000*(sorted(source)[len(source)/2]))
            iArray[3]=int(1000*max(source))
            aboutTimes[renameKey]=iArray
        tmpCalc('Connect','Connect')
        #tmpCalc('','Processing')
        tmpCalc('Waiting','Waiting')
        tmpCalc('Time taken for tests(not Run Time)','Total')
        retDict['Connection Times (ms)']=aboutTimes
        return retDict

    def getCondition(self):
        return self.getShowFormat(self.userCount,self.visitCount)

    @staticmethod
    def unitTest():
        pressurer=Pressurer('127.0.0.1:8000/admin',method='POST',userCount=10,visitCount=20)
        a=pressurer.getCondition()
        for key in a:
            print key,':',a[key]
        #print type(a)

                #for key in x:
                #    print key
                #break
                    #print key

if __name__=="__main__":
    Pressurer.unitTest()