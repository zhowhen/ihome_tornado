#  coding:utf-8
import config

print 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**config.mysql_options)