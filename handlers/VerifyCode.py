#  coding:utf-8
from .BaseHandler import BaseHandler
from utils.captcha.captcha import captcha
# from libs.yuntongxun.CCP import ccp
from utils.response_code import RET
from libs.yuntongxun.async_ccp import sendTemplateSMS
import tornado.gen
import logging
import constants
import random
import re


class ImageCodeHandler(BaseHandler):
    """
    图片验证码
    """
    def get(self, *args, **kwargs):
        code_id = self.get_argument('codeid')
        pre_code_id = self.get_argument('pcodeid')
        if pre_code_id:
            try:
                self.redis.delete("image_code_%s" % pre_code_id)
            except Exception as e:
                logging.error(e)
        # name 验证码名称
        # text 验证码文字
        # image 验证码图片
        name, text, image = captcha.generate_captcha()
        try:
            self.redis.setex("image_code_%s" % code_id, constants.IMAGE_CODE_EXPIRES_SECONDS, text)
        except Exception as e:
            logging.error(e)
            self.write('')
        self.set_header("Content-Type", "image/jpg")
        self.write(image)


# 异步的方式发送手机验证码
class PhoneCodeHandler(BaseHandler):
    """
    手机验证码
    """
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        # 获取参数
        # 判断图片验证码
        # 若成功
        # 发送短信
        mobile = self.json_args.get('mobile')
        image_code_id = self.json_args.get('image_code_id')
        image_code_text = self.json_args.get('image_code_text')

        # 检测参数是否完整
        self.check_args(mobile, image_code_id, image_code_text)

        # 手机号码验证
        if not re.match(r'1[34578]\d{9}', mobile):
           self.write_error(errno=RET.PARAMERR, errmsg='手机号码格式错误')

        # 判断图片验证码
        try:
            real_image_code_text = self.redis.get('image_code_%s' % image_code_id)
        except Exception as e:
            logging.error(e)
            self.write_error(errno=RET.DBERR, errmsg='redis查询错误')
            real_image_code_text = None
        if not real_image_code_text:
            self.write_error(errno=RET.NODATA, errmsg='验证码已过期')
        if real_image_code_text.upper() != image_code_text.upper():
            self.write_error(errno=RET.DATAERR, errmsg='验证码错误')

        # 验证图片验证码成功后，生成随机短信验证码
        sms_code = '%04d' % random.randint(0, 9999)
        try:
            self.redis.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRES_SECONDS, sms_code)
        except Exception as e:
            logging.error(e)
            self.write_error(errno=RET.DBERR, errmsg='生成短信验证码错误')

        # 异步发送短信
        res = yield sendTemplateSMS(mobile, [sms_code, constants.SMS_CODE_EXPIRES_SECONDS/60], 1)
        # 验证短信是否发送成功
        if res.get('statusCode') != '000000':
           self.write_error(errno=RET.THIRDERR, errmsg=res.get('statusMsg'))
        # 成功 返回OK
        self.write(dict(errno=RET.OK, errmsg='OK'))


# 同步的方式发送短信验证码
# class PhoneCodeHandler(BaseHandler):