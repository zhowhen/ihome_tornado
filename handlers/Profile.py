#  coding:utf-8
import logging
import config
from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.image_storage import storage
from model.ihome import ihome_model
from utils.commons import require_login


class CheckLoginHandler(BaseHandler):
    """"""
    def get(self, *args, **kwargs):
        # get_current_user方法在基类中已实现，它的返回值是session.data（用户保存在redis中
        # 的session数据），如果为{} ，意味着用户未登录;否则，代表用户已登录
        if self.get_current_user():
            return self.write(dict(errno=RET.OK, errmsg='OK', data=dict(name=self.session.data.get('name'))))
        else:
            return self.write(dict(errno=RET.SESSIONERR, errmsg='用户未登录'))


class ProfileHandler(BaseHandler):
    """"""
    @require_login
    def get(self, *args, **kwargs):
        # 获取用户id
        user_id = self.session.data.get('user_id')

        # 获取用户信息
        ih_user_profile = ihome_model('ih_user_profile')
        try:
            res = self.db.query(ih_user_profile.up_name, ih_user_profile.up_mobile, ih_user_profile.up_avatar).\
                filter(ih_user_profile.up_user_id == user_id).first()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='获取用户信息失败'))

        if not res:
            return self.write(dict(errno=RET.DATAERR, errmsg='用户不存在'))
        data = dict(
            name = res.up_name,
            mobile = res.up_mobile,
            avatar = config.image_url_prefix+res.up_avatar
        )
        self.write(dict(errno=RET.OK, errmsg='OK', data=data))


class AvatarHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        try:
            image_data = self.request.files['avatar'][0]['body']
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.PARAMERR, errmsg='参数错误'))
        # 检查参数
        self.check_args(image_data)

        # 上传七牛云空间
        try:
            image_name = storage(image_data)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.THIRDERR, errmsg='头像上传七牛错误'))

        # 更新数据库
        user_id = self.session.data.get('user_id')
        ih_user_profile = ihome_model('ih_user_profile')
        item = dict(up_avatar=image_name)
        try:
            self.db.query(ih_user_profile).filter(ih_user_profile.up_user_id == user_id).update(item)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='保存用户头像失败'))

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK', data='%s%s' % (config.image_url_prefix, image_name)))


class NameHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        name = self.json_args.get('name')

        # 检查参数
        self.check_args(name)

        # 更新数据库
        user_id = self.session.data.get('user_id')
        ih_user_profile = ihome_model('ih_user_profile')
        item = dict(up_name=name)
        try:
            self.db.query(ih_user_profile).filter(ih_user_profile.up_user_id == user_id).update(item)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='保存用户昵称失败'))

        # 更新session中的name
        try:
            self.session.data['name'] = name
            self.session.save()
        except Exception as e:
            logging.error(e)

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK'))