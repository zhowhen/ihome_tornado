#  coding:utf-8

from sqlalchemy import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_engine import ihome_engine
BaseModel = declarative_base()


# 定义一个方法用来把数据库的表映射过来
def ihome_model(tableName):
    class BaseClass(BaseModel):
        __tablename__ = tableName
        metadata = MetaData(bind=ihome_engine)

        # 把表映射过来
        Table(__tablename__, metadata, autoload=True)

    #     @classmethod
    #     def instance(cls):
    #         if not hasattr(cls, '_instance'):
    #             cls._instance = cls()
    #         return cls._instance
    #
    # baseclass = BaseClass.instance()
    return BaseClass
