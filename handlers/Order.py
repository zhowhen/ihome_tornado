#  coding:utf-8

from .BaseHandler import BaseHandler
from utils.commons import require_login
from model.ihome import ihome_model
from utils.commons import RET
from datetime import datetime
from sqlalchemy import func
import logging


class OrderHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        user_id = self.session.data.get('user_id')
        house_id = self.json_args.get('house_id')
        start_date = self.json_args.get('start_date')
        end_date = self.json_args.get('end_date')

        # 验证参数
        self.check_args(user_id, house_id, start_date, end_date)
        # 对时间进行格式化
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # 开始日期不能大于结束日期
        days = int((end_date - start_date).days) + 1
        if days <= 0:
            return self.write(dict(errno=RET.PARAMERR, errmsg='日期格式错误'))

        ih_house_info = ihome_model('ih_house_info')
        ih_order_info = ihome_model('ih_order_info')

        # 判断下单是否为房东本人，如果是房东拒绝操作
        try:
            ret = self.db.query(ih_house_info.hi_user_id,
                                ih_house_info.hi_price).\
                filter(ih_house_info.hi_house_id == house_id).first()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='查询出错'))

        if not ret:
            return self.write(dict(errno=RET.DATAERR, errmsg='没有数据'))

        if ret.hi_user_id == user_id:
            return self.write(dict(errno=RET.ROLEERR, errmsg='拒绝此操作'))

        house_priec = ret.hi_price
        # 判断日期内是否有订单
        if start_date > end_date:
            return self.write(dict(errno=RET.DATAERR, errmsg='日期错误'))
        # 查询数据库里当前房屋此时间段有没有订单
        try:
            ret = self.db.query(func.count('*')).filter(ih_order_info.oi_house_id == house_id,
                                                        ih_order_info.oi_begin_date < end_date,
                                                        ih_order_info.oi_end_date > start_date).scalar()
        except Exception as e:
            logging.error(e)
        else:
            if ret:
                return self.write(dict(errno=RET.DATAERR, errmsg='房子已租出'))

        # 更新数据
        item = dict(
            oi_user_id=user_id,
            oi_house_id=house_id,
            oi_begin_date=start_date,
            oi_end_date=end_date,
            oi_days=days,
            oi_house_price=house_priec,
            oi_amount=days*house_priec
        )
        try:
            self.db.execute(ih_order_info.__table__.insert(), item)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='生成订单失败'))

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK'))