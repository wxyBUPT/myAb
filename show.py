#coding=utf-8
'''
用来展示的模块，包括将获得的数据显示到屏幕，
将获得的数据存储到csv中，将数据存储到一个新的html文件中
以及保存为tsv文件
'''
__author__ = 'xiyuanbupt'
from abLog import logger

class Show(object):
    '''
    用来展示结果的类
    打算写成一个比较通用的类，
    与数据无关只与结构有关
    '''
    def __init__(self,resDict,exceptList=[],showOrder=[]):
        '''
        用表示结果的字典初始化，并可以设定不用来显示的项
        :param resDict: 用来显示的数据，类json的字典
        :param exceptList: 用来设定不显示的key值得
        :param showOrder: 可选参数，用来指定显示的顺序
        :return:
        '''
        self.exceptList=exceptList
        def initResDict(resDict,exceptList):
            '''
            用来初始化需要显示的字典
            :param resDict:
            :param exceptList:
            :return:
            '''
            retDict={}
            for item in resDict:
                if item not in exceptList:
                    retDict[item]=resDict[item]
            return retDict
        def initShowOrder(resDict,showOrder):
            resOrder=[]
            if showOrder==[]:
                for item in resDict:
                    resOrder.append(item)
            else:
                for item in showOrder:
                    if resDict.has_key(item):
                        resOrder.append(item)
            return resOrder
        self.resDict=initResDict(resDict,exceptList)
        self.showOrder=initShowOrder(self.resDict,showOrder)
        self.data=self.getTabData(self.resDict,self.showOrder)

    def outToStdout(self):
        '''
        将结果显示到标准输出
        如果有{key:value}中的type(value)为dict，则将这种显示到最后
        :return:
        '''
        lastDict={}
        for key in self.showOrder:
            if type(self.resDict[key])!=type({}):
                print '%-20s : %-20s'%(key,self.resDict[key])
            else:
                lastDict[key]=self.resDict[key]
        for key in lastDict:
            print ''
            print key
            tmp=lastDict[key]
            for key in tmp:
                outStr='%-10s'%(key)
                for ss in tmp[key]:
                    outStr=outStr+'%-10s'%(ss)
                print outStr
        return True

    def getTabData(self,resDict,showOrder):
        '''
        返回tablib.Dataset实例，用来后续的格式处理
        :param resDict:
        :param showOrder:
        :return:
        '''
        import tablib
        lastDict={}
        headers=('Attribute','value')
        data=[]
        for key in showOrder:
            if type(self.resDict[key])!=type({}):
                line=(key,resDict[key])
                data.append(line)
            else:
                lastDict[key]=resDict[key]
        for key in lastDict:
            data.append(())
            data.append((key,))
            tmp=lastDict[key]
            for key in tmp:
                line=[key,]
                line.extend(tmp[key])
                line=tuple(line)
                data.append(line)
        return tablib.Dataset(*data,headers=headers)

    def outToCSV(self,filename):
        '''
        将结果输出到CSV中，
        :param filename: 将要生成CSV文件的名
        :return:
        '''
        f=open(filename,'wb')
        f.write(self.data.csv)
        f.close()
        return True

    def outToHTML(self,filename):
        '''
        将结果输出为html文件
        :param filename:
        :return:
        '''
        f=open(filename,'wb')
        f.write(self.data.html)
        f.close()
        return True

    def outToTSV(self,filename):
        '''
        将结果输出为tsv文件
        :param filename:
        :return:
        '''
        f=open(filename,'wb')
        f.write(self.data.tsv)
        f.close()
        return True