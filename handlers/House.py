#  coding:utf-8

from .BaseHandler import BaseHandler
from utils.response_code import RET
from model.ihome import ihome_model
import constants
import logging
import json


class AreaInfoHandler(BaseHandler):
    """"""
    def get(self, *args, **kwargs):
        # 从redis里面取
        try:
            ret = self.redis.get('area_info')
        except Exception as e:
            logging.error(e)
            ret = None

        if ret:
            logging.info("hit redis")
            logging.debug(ret)
            return self.write('{"errno":%s,"errmsg":"OK","data":%s}' % (RET.OK, ret))

        # redis中如果没有就从数据库中取
        ih_area_info = ihome_model("ih_area_info")
        try:
            ret = self.db.query(ih_area_info.ai_area_id, ih_area_info.ai_name).all()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='查询区域信息数据库出错'))

        if not ret:
            return self.write(dict(errno=RET.NODATA, errmsg='无区域信息'))

        data = []
        for i in ret:
            item = {
                'area_id': i.ai_area_id,
                'name': i.ai_name
            }
            data.append(item)

        # 将数据库取得的数据存入redis
        try:
            self.redis.setex('area_info', constants.AREA_INFO_EXPIRES_SECONDS, json.dumps(data))
        except Exception as e:
            logging.error(e)

        self.write(dict(errno=RET.OK, errmsg='OK', data=data))