"""
mongodb 数据库接口的简单包装器
"""

from pymongo import MongoClient

# 全局客户端
client = None


def store(host, db, collection, documents):
    """
    存储给定的文档到指定的数据库
    :param host: 目标主机
    :param db: 目标数据库
    :param collection: 目标集合
    :param documents: 待存储的文档
    :return:
    """
    global client

    # 如果客户端为空，则构造
    if client is None:
        client = MongoClient(host)

    try:
        if isinstance(documents, list):
            # 插入多文档
            client[db][collection].insert_many(documents)
        else:
            # 插入单文档
            client[db][collection].insert_one(documents)
    except Exception as e:
        # 数据库异常
        print('DB error:%s' % e.__cause__)
        client.close()
        client = None
