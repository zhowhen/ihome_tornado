#  coding:utf-8

from .BaseHandler import BaseHandler
from utils.response_code import RET
from model.ihome import ihome_model
from utils.commons import require_login
from utils.image_storage import storage
import constants
import config
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


class MyHousesHandler(BaseHandler):
    """"""
    @require_login
    def get(self, *args, **kwargs):

        # 获取用户id
        user_id = self.session.data['user_id']

        # 数据库中取数据
        ih_house_info = ihome_model('ih_house_info')
        ih_area_info = ihome_model('ih_area_info')
        try:
            ret = self.db.query(ih_house_info.hi_house_id,
                                ih_house_info.hi_title,
                                ih_house_info.hi_price,
                                ih_house_info.hi_ctime,
                                ih_area_info.ai_name,
                                ih_house_info.hi_index_image_url).\
                filter(ih_house_info.hi_user_id == user_id, ih_house_info.hi_area_id == ih_area_info.ai_area_id).all()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='查询数据库出错'))

        # 构建返回数据列表
        houses = []
        if ret:
            for i in ret:
                item = dict(
                    house_id=i.hi_house_id,
                    title=i.hi_title,
                    area_name=i.ai_name,
                    price=i.hi_price,
                    img_url=config.image_url_prefix + i.hi_index_image_url if i.hi_index_image_url else '',
                    ctime=i.hi_ctime.strftime('%Y-%m-%d %H:%M:%S'),
                )
                houses.append(item)

        self.write(dict(errno=RET.OK, errmsg='OK', houses=houses))


class HouseInfoHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        user_id = self.session.data.get('user_id')
        # user_id = 10005
        title = self.json_args.get('title')
        price = self.json_args.get('price')
        area_id = self.json_args.get('area_id')
        address = self.json_args.get('address')
        room_count = self.json_args.get('room_count')
        acreage = self.json_args.get('acreage')
        unit = self.json_args.get('unit')
        capacity = self.json_args.get('capacity')
        beds = self.json_args.get('beds')
        deposit = self.json_args.get('deposit')
        min_days = self.json_args.get('min_days')
        max_days = self.json_args.get('max_days')
        facility = self.json_args.get('facility')

        # 验证参数
        self.check_args(title, price, area_id, address,
                        room_count, acreage, unit, capacity,
                        beds, deposit, min_days, max_days, facility)
        try:
            price = int(price)*100
            deposit = int(deposit)*100
            capacity = int(capacity)
            room_count = int(room_count)
            acreage = int(acreage)
            min_days = int(min_days)
            max_days = int(max_days)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.PARAMERR, errmsg='参数错误'))

        # 数据库操作
        ih_house_info = ihome_model('ih_house_info')
        ih_house_facility = ihome_model('ih_house_facility')
        item = dict(
            hi_user_id=user_id,
            hi_title=title,
            hi_price=price,
            hi_area_id=area_id,
            hi_address=address,
            hi_room_count=room_count,
            hi_acreage=acreage,
            hi_house_unit=unit,
            hi_capacity=capacity,
            hi_beds=beds,
            hi_deposit=deposit,
            hi_min_days=min_days,
            hi_max_days=max_days,
        )
        try:
            res = self.db.execute(ih_house_info.__table__.insert(), item)
            fac = []
            for i in facility:
                tem = dict(
                    hf_house_id=res.lastrowid,
                    hf_facility_id=i
                )
                fac.append(tem)
            self.db.execute(ih_house_facility.__table__.insert(), fac)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='save data error'))

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='ok', house_id=res.lastrowid))

    def get(self, *args, **kwargs):
        # 获取参数
        house_id = self.get_argument('house_id')

        # 验证参数
        self.check_args(house_id)

        # 从数据库取出数据
        # 数据库中取数据
        ih_house_info = ihome_model('ih_house_info')
        ih_user_profile = ihome_model('ih_user_profile')
        ih_area_info = ihome_model('ih_area_info')
        ih_house_facility = ihome_model('ih_house_facility')
        ih_house_image = ihome_model('ih_house_image')
        ih_order_info = ihome_model('ih_order_info')
        # 查询房屋基本信息
        try:
            ret = self.db.query(ih_house_info.hi_house_id,
                                ih_house_info.hi_user_id,
                                ih_house_info.hi_title,
                                ih_house_info.hi_price,
                                ih_house_info.hi_ctime,
                                ih_area_info.ai_name,
                                ih_user_profile.up_avatar,
                                ih_user_profile.up_name,
                                ih_house_info.hi_address,
                                ih_house_info.hi_room_count,
                                ih_house_info.hi_acreage,
                                ih_house_info.hi_house_unit,
                                ih_house_info.hi_capacity,
                                ih_house_info.hi_beds,
                                ih_house_info.hi_deposit,
                                ih_house_info.hi_min_days,
                                ih_house_info.hi_max_days,
                                ). \
                filter(ih_house_info.hi_house_id == house_id,
                       ih_house_info.hi_user_id == ih_user_profile.up_user_id,
                       ih_house_info.hi_area_id == ih_area_info.ai_area_id,
                       ).first()
        except Exception as e:
            logging.error(e)
            ret = None
        if not ret:
            return self.write(dict(errno=RET.DBERR, errmsg='查询数据库出错'))

        data = dict(
            price=ret.hi_price,
            title=ret.hi_title,
            user_avatar=config.image_url_prefix + ret.up_avatar if ret.up_avatar else '',
            user_id=ret.hi_user_id,
            user_name=ret.up_name,
            address=ret.hi_address,
            room_count=ret.hi_room_count,
            acreage=ret.hi_acreage,
            unit=ret.hi_house_unit,
            capacity=ret.hi_capacity,
            beds=ret.hi_beds,
            deposit=ret.hi_deposit,
            min_days=ret.hi_min_days,
            max_days=ret.hi_max_days,
        )
        # 查询房屋图片信息
        try:
            ret = self.db.query(ih_house_image.hi_url).\
                filter(ih_house_image.hi_house_id == house_id).all()
        except Exception as e:
            logging.error(e)
            ret = []
        img_list = []
        if ret:
            img_list = map(lambda x: config.image_url_prefix + str(x.hi_url), ret)
        data['images'] = img_list
        # 查询房屋设施信息
        try:
            ret = self.db.query(ih_house_facility.hf_facility_id).\
                filter(ih_house_facility.hf_house_id == house_id).all()
        except Exception as e:
            logging.error(e)
            ret = []
        facilities = []
        if ret:
            # 查询结果为[(1,), (2,), (3,), (9,), (13,), (14,), (15,), (21,), (22,), (23,)]
            # 转化成['1', '2', '3', '9', '13', '14', '15', '21', '22', '23']
            facilities = map(lambda x: x.hf_facility_id, ret)
        data['facilities'] = facilities

        # 查询房屋评论
        try:
            ret = self.db.query(ih_order_info.oi_comment,
                                ih_order_info.oi_utime,
                                ih_user_profile.up_name,
                                ih_user_profile.up_mobile).\
                filter(ih_order_info.oi_house_id == house_id,
                       ih_order_info.oi_status == 4,
                       ih_order_info.oi_user_id == ih_user_profile.up_user_id).all()
        except Exception as e:
            logging.error(e)
            ret = []
        comments = []
        if ret:
            for i in ret:
                item = dict(
                    user_name=i.up_name if i.up_name != i.up_mobile else '匿名用户',
                    ctime=i.oi_utime,
                    content=i.oi_comment
                )
                comments.append(item)
        data['comments'] = comments
        # 返回结果
        self.write(dict(errno=RET.OK, errmsg='OK', data=data))


class HouseImageHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        house_id = self.get_argument('house_id')
        try:
            image_data = self.request.files['house_image'][0]['body']
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
            image_name = None

        if not image_name:
            return self.write(dict(errno=RET.THIRDERR, errmsg='房屋图片上传七牛错误'))

        # 保存到数据库
        # 保存图片路径到数据库ih_house_image表,并且设置房屋的主图片(ih_house_info中的hi_index_image_url）
        # 我们将用户上传的第一张图片作为房屋的主图片
        ih_house_info = ihome_model('ih_house_info')
        ih_house_image = ihome_model('ih_house_image')
        item = dict(hi_house_id=house_id, hi_url=image_name)
        try:
            self.db.execute(ih_house_image.__table__.insert(), item)
            self.db.query(ih_house_info).\
                filter(ih_house_info.hi_house_id == house_id, ih_house_info.hi_index_image_url == None).\
                update(dict(hi_index_image_url=image_name))
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.THIRDERR, errmsg='save data error'))
        # 返回数据
        img_url = config.image_url_prefix + image_name
        self.write(dict(errno=RET.OK, errmsg='OK', url=img_url))
