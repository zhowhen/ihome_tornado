#  coding:utf-8
from sqlalchemy import create_engine
import config

# 创建一个引擎
ihome_engine = create_engine(
    'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'.format(**config.mysql_options),
    encoding='utf-8',
    echo=True,
    pool_size=1000,
    pool_recycle=7200,
    # autocommit=True,
    connect_args={'charset': 'utf8'}  # 设置数据库字符编码
)
