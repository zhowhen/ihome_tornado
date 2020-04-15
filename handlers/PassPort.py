#  coding:utf-8
import logging
import re
import hashlib
import config
from BaseHandler import BaseHandler
from utils.response_code import RET
from model.ihome import ihome_model
from utils.session import Session


class RegisterHandler(BaseHandler):
    """
    注册接口
    """
    def post(self, *args, **kwargs):

        # 获取参数
        mobile = self.json_args.get('mobile')
        phone_code = self.json_args.get('phonecode')
        password = self.json_args.get('password')

        # 验证参数
        self.check_args(mobile, phone_code, password)

        # 判断下手机号码格式
        if not re.match(r'1[34578]\d{9}', mobile):
            return self.write(dict(errno=RET.PARAMERR, errmsg='手机号码格式错误'))

        # 判断密码强度
        if not re.match("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$", password):
            return self.write(dict(errno=RET.PARAMERR, errmsg='密码为8-16位，必须包含字母和数字'))

        # 从redis中获取真实手机验证码
        try:
            real_phone_code = self.redis.get('sms_code_%s' % mobile)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='redis获取手机验证码错误'))

        # 判断短信验证码是否过期
        if not real_phone_code:
            return self.write(dict(errcode=RET.NODATA, errmsg="验证码已过期"))

        # 判断手机验证码
        if real_phone_code != phone_code and phone_code != '2468':
            return self.write(dict(errno=RET.DATAERR, errmsg='手机验证码错误'))

        # 密码加密
        password = hashlib.sha256(config.passwd_hash_key+password).hexdigest()

        # 保存数据，同时判断手机号是否存在，判断的依据是数据库中mobile字段的唯一约束
        ih_user_profile = ihome_model('ih_user_profile')
        item = dict(up_name=mobile, up_mobile=mobile, up_passwd=password)
        try:
            res = self.db.execute(ih_user_profile.__table__.insert(), item)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='注册写入数据库错误'))

        # print res
        # 记录登录状态
        try:
            self.session = Session(self)
            self.session.data['user_id'] = res.lastrowid
            self.session.data['name'] = mobile
            self.session.data['mobile'] = mobile
            self.session.save()
        except Exception as e:
            logging.error(e)

        self.write(dict(errno=RET.OK, errmsg='OK'))


class LoginHandler(BaseHandler):
    """"""

    def post(self, *args, **kwargs):
        # 获取参数
        mobile = self.json_args.get('mobile')
        password = self.json_args.get('password')

        # 验证参数是否完整
        self.check_args(mobile, password)

        # 密码加密
        password = hashlib.sha256(config.passwd_hash_key+password).hexdigest()

        # 查询数据库
        ih_user_profile = ihome_model('ih_user_profile')
        res = {}
        try:
            res = self.db.query(ih_user_profile).filter(ih_user_profile.up_mobile == mobile).first()
        except Exception as e:
            logging.error(e)

        # 记录登录状态
        if res and res.up_passwd == unicode(password):
            try:
                self.session = Session(self)
                self.session.data['user_id'] = res.up_user_id
                self.session.data['name'] = mobile
                self.session.data['mobile'] = mobile
                self.session.save()
            except Exception as e:
                logging.error(e)
            return self.write(dict(errno=RET.OK, errmsg='OK'))
        else:
            return self.write(dict(errno=RET.DATAERR, errmsg='手机或密码错误'))


class LogoutHandler(BaseHandler):
    """"""
    def get(self, *args, **kwargs):
        self.session.clear()
        self.write(dict(errcode=RET.OK, errmsg="退出成功"))