#  coding:utf-8
from handlers import PassPort, VerifyCode, Profile, House, Order
from handlers.BaseHandler import StaticFileHandler
import os

handlers = [
    (r'^/api/imagecode$', VerifyCode.ImageCodeHandler),
    (r'^/api/smscode$', VerifyCode.PhoneCodeHandler),

    (r'^/api/register$', PassPort.RegisterHandler),
    (r'^/api/login$', PassPort.LoginHandler),
    (r'^/api/check_login$', PassPort.CheckLoginHandler),
    (r'^/api/logout$', PassPort.LogoutHandler),

    (r'^/api/profile$', Profile.ProfileHandler),
    (r'^/api/profile/avatar$', Profile.AvatarHandler),
    (r'^/api/profile/name$', Profile.NameHandler),
    (r'^/api/profile/auth$', Profile.AuthHandler),

    (r'^/api/house/area$', House.AreaInfoHandler),
    (r'^/api/house/info$', House.HouseInfoHandler),
    (r'^/api/house/image$', House.HouseImageHandler),
    (r'^/api/house/my$', House.MyHousesHandler),
    (r'^/api/house/list2$', House.HouseListHandler),
    (r'^/api/house/index$', House.HouseIndexHandler),

    (r'^/api/order$', Order.OrderHandler),
    (r'^/api/order/my$', House.HouseIndexHandler),
    (r'^/api/order/accept$', House.HouseIndexHandler),
    (r'^/api/order/reject$', House.HouseIndexHandler),
    (r'^/api/order/comment$', House.HouseIndexHandler),

    (r'/(.*)', StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__), 'html'),
                                       default_filename='index.html')),
]
