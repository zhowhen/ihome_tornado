#  coding:utf-8

from .BaseHandler import BaseHandler
from utils.commons import require_login
from model.ihome import ihome_model
from utils.commons import RET
from datetime import datetime
from sqlalchemy import func
import logging
import config


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
        # 没有房屋数据
        if not ret:
            return self.write(dict(errno=RET.DATAERR, errmsg='没有数据'))
        # 预定房间是房东本人
        if ret.hi_user_id == user_id:
            return self.write(dict(errno=RET.ROLEERR, errmsg='拒绝此操作'))

        house_priec = ret.hi_price

        # 判断日期内是否有订单
        # 查询数据库里当前房屋此时间段有没有订单
        try:
            ret = self.db.query(func.count('*')).filter(ih_order_info.oi_house_id == house_id,
                                                        ih_order_info.oi_begin_date < end_date,
                                                        ih_order_info.oi_end_date > start_date).scalar()
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "get date error"})
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


class MyOrdersHandler(BaseHandler):
    """"""
    @require_login
    def get(self, *args, **kwargs):
        # 获取参数
        user_id = self.session.data.get('user_id')

        # 获取角色
        role = self.get_argument('role')

        # 检测参数
        self.check_args(role)

        # 查询数据库
        ih_order_info = ihome_model('ih_order_info')
        ih_house_info = ihome_model('ih_house_info')
        try:
            # 角色是用户
            if role == 'custom':
                ret = self.db.query(ih_order_info.oi_order_id,
                                    ih_order_info.oi_house_id,
                                    ih_order_info.oi_ctime,
                                    ih_order_info.oi_begin_date,
                                    ih_order_info.oi_end_date,
                                    ih_order_info.oi_comment,
                                    ih_order_info.oi_days,
                                    ih_order_info.oi_status,
                                    ih_order_info.oi_amount,
                                    ih_house_info.hi_title,
                                    ih_house_info.hi_index_image_url,
                                    ).filter(ih_order_info.oi_user_id == user_id,
                                             ih_order_info.oi_house_id == ih_house_info.hi_house_id).all()
            else:
                ret = self.db.query(ih_order_info.oi_order_id,
                                    ih_order_info.oi_house_id,
                                    ih_order_info.oi_ctime,
                                    ih_order_info.oi_begin_date,
                                    ih_order_info.oi_end_date,
                                    ih_order_info.oi_comment,
                                    ih_order_info.oi_days,
                                    ih_order_info.oi_status,
                                    ih_order_info.oi_amount,
                                    ih_house_info.hi_title,
                                    ih_house_info.hi_index_image_url,
                                    ).filter(ih_house_info.hi_user_id == user_id,
                                             ih_order_info.oi_house_id == ih_house_info.hi_house_id).all()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='查询出错'))

        # 构建返回数据
        order_list = []
        if ret:
            for i in ret:
                item = dict(
                    order_id=i.oi_order_id,
                    status=i.oi_status,
                    img_url=config.image_url_prefix+str(i.hi_index_image_url),
                    title=i.hi_title,
                    ctime=i.oi_ctime.strftime('%Y-%m-%d %H:%M:%S'),
                    start_date=i.oi_begin_date.strftime('%Y-%m-%d'),
                    end_date=i.oi_end_date.strftime('%Y-%m-%d'),
                    amount=i.oi_amount,
                    days=i.oi_days,
                    comment=i.oi_comment
                )
                order_list.append(item)
        logging.debug(order_list)

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK', orders=order_list))


class AcceptOrderHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        user_id = self.session.data.get('user_id')
        order_id = self.json_args.get('order_id')

        # 验证参数
        if not order_id:
            return self.write(dict(errno=RET.PARAMERR, errmsg='参数错误'))

        # 更新数据库
        ih_order_info = ihome_model('ih_order_info')
        ih_house_info = ihome_model('ih_house_info')
        try:
            self.db.query(ih_order_info).\
                filter(ih_order_info.oi_house_id.in_(self.db.query(ih_house_info.hi_house_id).
                                                     filter(ih_house_info.hi_user_id == user_id)),
                       ih_order_info.oi_status == 0,
                       ih_order_info.oi_order_id == order_id).\
                update(dict(oi_status=3), synchronize_session=False)
            # synchronize_session=False 代表直接进行更新操作
            # synchronize_session='fetch'代表先进行一次查询，然后再进行更新操作
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='update data error'))

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK'))

class RejectOrderHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        user_id = self.session.data.get('user_id')
        order_id = self.json_args.get('order_id')
        reject_reason = self.json_args.get('reject_reason')

        # 检测参数
        self.check_args(order_id, reject_reason)

        # 更新数据库
        ih_order_info = ihome_model('ih_order_info')
        ih_house_info = ihome_model('ih_house_info')
        try:
            self.db.query(ih_order_info). \
                filter(ih_order_info.oi_house_id.in_(self.db.query(ih_house_info.hi_house_id).
                                                     filter(ih_house_info.hi_user_id == user_id)),
                       ih_order_info.oi_status == 0,
                       ih_order_info.oi_order_id == order_id). \
                update(dict(oi_status=6, oi_comment=reject_reason), synchronize_session=False)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='update data error'))

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK'))


class OrderCommentHandler(BaseHandler):
    """"""
    @require_login
    def post(self, *args, **kwargs):
        # 获取参数
        user_id = self.session.data.get('user_id')
        order_id = self.json_args.get('order_id')
        comment = self.json_args.get('comment')

        # 验证参数
        self.check_args(order_id, comment)

        # 更新数据库
        ih_order_info = ihome_model('ih_order_info')

        try:
            self.db.query().filter(ih_order_info.oi_user_id == user_id,
                                   ih_order_info.oi_order_id == order_id,
                                   ih_order_info.oi_status == 3).update(dict(oi_comment=comment,
                                                                             oi_status=4))
            self.db.commit()
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg='update data error'))

        # 同步更新redis中的房屋评论信息，此处的策略是直接删除redis缓存中的该房屋数据
        try:
            ret = self.db.query(ih_order_info.oi_house_id).\
                query(ih_order_info.oi_order_id == order_id).first()

            if ret:
                try:
                    self.redis.delete('house_detail_%s' % ret.oi_house_id)
                except Exception as e:
                    logging.error(e)
        except Exception as e:
            logging.error(e)

        # 返回数据
        self.write(dict(errno=RET.OK, errmsg='OK'))