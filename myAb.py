#!/usr/bin/python
#coding=utf-8
'''
程序的入口函数，根据可选参数情况执行相应命令
并定义了一个全局的logger用于调试
'''
__author__ = 'xiyuanbupt'
VERSION=0.0
import sys,getopt
from abLog import logger
from pressurer import Pressurer
from show import Show

def ab():
    opts,args=getopt.getopt(sys.argv[1:],"A:C:c:d:n:eghHip:qsSv:Vwx:X:y:z:")
    logger.debug(u'ab被调用')
    for key in opts:
        logger.debug(key)
    if ('-h','') in opts:
        logger.debug(u'显示帮助信息')
        from data.help import helpDict
        for key in helpDict:
            print '%s   %s'%(key,helpDict[key])
    if ('-V','') in opts:
        logger.debug(u'请求版本号')
        print u'VERSION: %.1f'%VERSION
    optsDict=dict(opts)
    logger.debug(optsDict)
    opts=dict(opts)
    url=args[0]
    userCount=opts.get('-c',1)
    visitCount=opts.get('-n',1)
    userAgent=opts.get('-H',"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-Us) AppleWeb Kit/534.2 (KHTML, like Gecko) Chrome/6.0.447.0 Safari/534.2")
    outhString=opts.get('-A',None)
    cookie=opts.get('-C',None)
    postData=None
    proxy=None
    if opts.has_key('-p'):
        method='POST'
        postData=opts.get('-p',None)
    elif opts.has_key('-i'):
        method='HEAD'
    else:
        method='GET'
    if opts.has_key('-s'):
        protocal='https'
    else:
        protocal='http'
    if opts.has_key('-X'):
        proxy=opts.get('-X',None)
    else:
        pass
    parDict={}
    parDict['url']=url
    parDict['userCount']=int(userCount)
    parDict['visitCount']=int(visitCount)
    parDict['userAgent']=userAgent
    parDict['outhString']=outhString
    parDict['cookie']=cookie
    parDict['method']=method
    parDict['postData']=postData
    parDict['protocal']=protocal
    parDict['proxy']=proxy
    pressurer=Pressurer(**parDict)
    resault=pressurer.getCondition()

    #上面的resault为获得的结果，下面处理展示部分

    show=Show(resault)
    show.outToStdout()
    def createNameFor(suffix):
        import datetime
        return ('%s_user_%s_visit_host_%s_%s.%s'%(userCount,visitCount,url,datetime.datetime.now(),suffix)).replace(' ','_')
        pass
    if opts.has_key('-w'):
        fileName=createNameFor('html')
        print u'Create file %s'%fileName
        show.outToHTML(fileName)
    if opts.has_key('-g'):
        fileName=createNameFor('TSV')
        print u'Create file %s'%fileName
        show.outToTSV(fileName)
    if opts.has_key('-e'):
        fileName=createNameFor('csv')
        print u'Create file %s'%fileName
        show.outToCSV(fileName)

if __name__=="__main__":
    ab()