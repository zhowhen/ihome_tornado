#  coding:utf-8
# import config

# print 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**config.mysql_options)

l = [(1,), (2,), (3,), (9,), (13,), (14,), (15,), (21,), (22,), (23,)]
print map(lambda x:str(x[0]),l)