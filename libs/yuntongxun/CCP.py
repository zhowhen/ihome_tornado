#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8aaf07087162cd7801716959ab0701ea'

#���ʺ�Token
accountToken= 'a6eb7b9d6dcb4b6296480799b49101b3'

#Ӧ��Id
appId='8aaf07087162cd7801716959ab6901f0'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
_serverPort='8883'

#REST�汾��
_softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id
class _CCP(object):
    def __init__(self):
        # ��ʼ��REST SDK
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
#sendTemplateSMS(�ֻ�����,��������,ģ��Id)