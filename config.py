#  coding:utf-8
import os

# Application 配置参数
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "template_path": os.path.join(os.path.dirname(__file__), 'template'),
    "cookie_secret": "n1jjld6rQF2r58IhjQRy2FGC2VaU8kFFr4mf7FUcr6w=",
    "xsrf_cookies": True,
    "debug": True,
}

# mysql
mysql_options = dict(
    host="106.52.238.231",
    database="ihome",
    user="root",
    password="*****",
    port=3306,
)

# redis
redis_options = dict(
    host="106.52.238.231",
    port=6379,
    password='******'
)

# log file
log_level = 'debug'
log_file = r'E:\github\logs\log'

# session
session_expires_second = 86400  # session有效期（s）

# 密码加密   盐值
passwd_hash_key = 'n1jjld6rQF2r58IhjQRy2FdC2gaU8kFFr4mf7FUcr6w='

# 七牛图片的域名
image_url_prefix = 'http://q8iwsevuq.bkt.clouddn.com/'
