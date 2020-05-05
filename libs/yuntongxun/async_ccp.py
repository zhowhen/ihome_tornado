#  coding:utf-8
import datetime
import md5
import base64
from tornado.httpclient import AsyncHTTPClient
import tornado.gen
import json

base_url = 'https://app.cloopen.com:8883/'

# 主帐号
accountSid = '8aaf07087162cd7801716959ab0701ea'

# 主帐号Token
accountToken = 'a6eb7b9d6dcb4b6296480799b49101b3'

# 应用Id
appId = '8aaf07087162cd7801716959ab6901f0'

# REST版本号
_softVersion = '2013-12-26'


@tornado.gen.coroutine
def sendTemplateSMS(to, datas, tempId=1):
    http = AsyncHTTPClient()

    nowdate = datetime.datetime.now()
    Batch = nowdate.strftime("%Y%m%d%H%M%S")
    # 生成sig
    signature = accountSid + accountToken + Batch
    sig = md5.new(signature).hexdigest().upper()
    # 拼接URL
    url = base_url + _softVersion + "/Accounts/" + accountSid + "/SMS/TemplateSMS?sig=" + sig
    # 生成auth
    src = accountSid + ":" + Batch
    auth = base64.encodestring(src).strip()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8',
        'Content-Length': 256,
        'Authorization': auth
    }
    body = {
        "to": to,
        "appId": appId,
        "templateId": tempId,
        "datas": datas
    }
    response = yield http.fetch(url, method='POST', body=json.dumps(body), headers=headers)
    print response
    if response.error:
        rep = {'error': response.error}
    else:
        rep = json.loads(response.body)
    raise tornado.gen.Return(rep)
