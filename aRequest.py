#coding=utf-8
__author__ = 'xiyuanbupt'
import pycurl
import StringIO
import time
from abLog import logger
class ARequset(object):
    def __init__(self,method,url,header,postData=None,proxy=None):
        '''

        :param method: 方法，POST或者GET，或者HEAD等
        :param url: 请求的url，包含http头
        :param header: 请求头
        :param postData: 如果请求方法为post则包含编码好的postData
        :return:
        '''
        self.method=method
        self.url=url
        self.header=header
        self.postData=postData
        self.proyx=proxy
        self.IO=StringIO.StringIO()
        self.response=self.perform()

    def __del__(self):
        '''
        释放资源
        :return:
        '''
        self.IO.close()
        self.response.close()

    def perform(self):
        c=pycurl.Curl()
        c.setopt(c.URL,self.url)
        c.setopt(c.WRITEFUNCTION,self.IO.write)
        c.setopt(c.FOLLOWLOCATION,1)
        if cmp(self.method,'post')==1:
            c.setopt(c.POSTFIELDS,self.postData)
        c.setopt(c.MAXREDIRS,5)
        c.setopt(c.CONNECTTIMEOUT,60)
        c.setopt(c.HEADER,True)
        c.setopt(c.HTTPHEADER,self.header)
        if self.proyx is not None:
            c.setopt(c.PROXY,self.proyx)
        c.perform()
        return c

    def getInfo(self):
        '''
        获得一个请求目前能够获得的一切属性
        :return:
        '''
        info={}
        attris=dir(pycurl)
        for attri in attris:
            if hasattr(pycurl,attri):
                try:
                    info[attri.capitalize()]=self.response.getinfo(getattr(self.response,attri))
                except:
                    pass
        responseValue=self.IO.getvalue()
        if not info.has_key('Server'):
            info['Server']=self.getAttri(pattern='Server',text=responseValue)
        return info

    def getAttri(self,pattern='',text=''):
        '''
        获得指定的属性，假设有些属性是从返回文档中获得的
        :param pattern:
        :param text:
        :return:
        '''
        import re
        pattern='^'+pattern
        pat=re.compile(pattern,re.I)
        lines=text.split('\n')
        for line in lines:
            if re.match(pat,line):
                return line.split(':')[1].strip()
        return ''

    def getABParDic(self):
        '''
        获得ab程序需要参数的字典
        :return:
        '''
        info=self.getInfo()
        logger.debug(info)
        abDict={}
        abDict['Server Software']=info.get('Server','')
        abDict['Server Hostname']=info.get('Effective_url','').split('/')[2]
        abDict['Server IP']=info.get('Primary_ip','')
        abDict['Server Port']=info.get('Primary_port','')
        abDict['Document Path']='/'+('/').join(info.get('Effective_url','').split('/')[3:])
        downloadSize=info.get('Size_download',0)
        abDict['Total transferred']=downloadSize
        content_type=info.get('Content_type','')
        import re
        if re.search('html',content_type):
            abDict['HTML transferred']=downloadSize-info.get('Header_size',0)
        abDict['Document Length']=downloadSize-info.get('Header_size',0)
        abDict['Http_code']=info.get('Http_code',0)
        abDict['Time taken for tests']=info.get('Total_time',0)
        abDict['Name lookup time']=info.get('Namelookup_time',0)
        abDict['Waiting']=info.get('Starttransfer_time',0)
        abDict['Connect']=info.get('Connect_time',0)
        logger.debug(abDict)
        return abDict

    @staticmethod
    def unitTest():
        method='post'
        url='http://www.baidu.com'
        header=[]
        aRequest=ARequset(method,url,header)
        abDict=aRequest.getABParDic()
        for key in abDict:
            print key,':',abDict[key]

if __name__=="__main__":
    ARequset.unitTest()