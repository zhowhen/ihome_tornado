#  coding:utf-8
from utils.response_code import RET
from functools import wraps


def require_login(fun):
    @wraps(fun)
    def wrapper(request_handler_obj, *args, **kwargs):
        # 根据get_current_user方法判断，返回不为空，证明用户已经登录过，保存了session数据
        if request_handler_obj.get_current_user():
            fun(request_handler_obj, *args, **kwargs)
        # 返回为空字典，代表用户没有登录过，没有保存用户的session数据
        else:
            request_handler_obj.write(dict(errno=RET.SESSIONERR, errmsg='用户未登录'))
    return wrapper