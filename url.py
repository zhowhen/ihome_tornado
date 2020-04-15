#  coding:utf-8
from handlers import PassPort, VerifyCode, Profile
from handlers.BaseHandler import StaticFileHandler
import os

handlers = [
    (r'/api/imagecode', VerifyCode.ImageCodeHandler),
    (r'/api/smscode', VerifyCode.PhoneCodeHandler),
    (r'/api/register', PassPort.RegisterHandler),
    (r'/api/login', PassPort.LoginHandler),
    (r'/api/logout', PassPort.LogoutHandler),
    (r'/api/check_login', Profile.CheckLoginHandler),
    (r'/api/profile', Profile.ProfileHandler),
    (r'/api/profile/avatar', Profile.AvatarHandler),
    (r'/api/profile/name', Profile.NameHandler),

    (r'/(.*)', StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__), 'html'),
                                       default_filename='index.html')),
]
