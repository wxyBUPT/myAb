#coding=utf-8
'''
定义了一个logger
'''
__author__ = 'xiyuanbupt'
import logging
import logging.handlers

def getLogger(log_file='ab.log',maxBytes=1024*1024,backupCount=5,fmt='%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s',level=logging.DEBUG):
    handler=logging.handlers.RotatingFileHandler(filename=log_file,maxBytes=maxBytes,backupCount=backupCount)
    formatter=logging.Formatter(fmt)
    handler.setFormatter(formatter)
    loggerName=log_file.split('.')[0]
    logger=logging.getLogger(loggerName)
    logger.addHandler(handler)
    logger.setLevel(level=level)
    return logger

logger=getLogger()

