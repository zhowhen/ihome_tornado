#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8aaf07087162cd7801716959ab0701ea'

#主帐号Token
accountToken= 'a6eb7b9d6dcb4b6296480799b49101b3'

#应用Id
appId='8aaf07087162cd7801716959ab6901f0'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
_serverPort='8883'

#REST版本号
_softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id
class _CCP(object):
    def __init__(self):
        # 初始化REST SDK
        self.rest = REST(serverIP, _serverPort, _softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def sendTemplateSMS(self, to, datas, tempId):
        return self.rest.sendTemplateSMS(to, datas, tempId)

ccp = _CCP.instance()

if __name__ == '__main__':
    result = ccp.sendTemplateSMS(15575958395, ['1234', 5], 1)
    print result
    for k, v in result.iteritems():

        if k == 'templateSMS':
            for k, s in v.iteritems():
                print '%s:%s' % (k, s)
        else:
            print '%s:%s' % (k, v)
#sendTemplateSMS(手机号码,内容数据,模板Id)