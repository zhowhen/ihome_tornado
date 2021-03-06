#  coding:utf-8
import json
import tornado
from tornado.web import RequestHandler
from utils.response_code import RET
from utils.session import Session


class BaseHandler(RequestHandler):
    """
    handler 基类
    """
    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def check_args(self, *args):
        if not all(args):
            self.write(dict(errno=RET.PARAMERR, errmsg='参数不完整'))
            raise self.finish()

    def prepare(self):
        self.xsrf_token
        if self.request.headers.get('Content-Type', '').startswith('application/json'):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    def write_error(self, **kwargs):
        print kwargs
        self.write(kwargs)
        raise self.finish()

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def initialize(self):
        pass

    def on_finish(self):
        self.db.close()

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data


class StaticFileHandler(tornado.web.StaticFileHandler):
    """"""
    def __init__(self, *args, **kwargs):
        super(StaticFileHandler, self).__init__(*args, **kwargs)