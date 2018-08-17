"""
行情视图
"""

from dwebsocket import accept_websocket
from django.http import HttpResponse
from pymongo import MongoClient
from wsserver.quotation import config
from wsserver.quotation import utils
import json


@accept_websocket
def get_quots(request):
    """
    维持websocket连接，进行行情数据推送
    :param request: 传入的请求
    :return: 如果是websocket请求，则建立长连接，不返回；否则，返回包含错误信息的HttpResponse对象
    """
    # websocket请求
    if request.is_websocket():
        # 获取websocket实例
        ws = request.websocket

        # 获取交易所
        exchange = utils.get_exchange(request)

        if exchange != '':
            db_client = None

            try:
                # 构造数据库客户端对象
                db_client = build_db_client(exchange)

                # 获取目标数据库集合对象
                target_collection = get_target_collection(db_client, exchange)

                # 推送数据库中的最新数据
                push_latest_quots(ws, target_collection)

                # 数据库更新监视
                watch_db_insert(ws, target_collection)
            except Exception as e:
                on_error(ws, db_client, e.__cause__)

        # 请求参数错误
        else:
            ws.close()

    # 禁止http请求
    else:
        return HttpResponse("Http request not allowed")


def build_db_client(exchange):
    """
    构造客户端，以便连接与交易所关联的数据库
    :param exchange: 与数据库关联的交易所名
    :return: 如果exchange有效，则返回一个MongoClient对象;否则返回None
    """
    db_client = None

    if exchange in config.mongodb_conf.keys():
        # 获取配置数据
        target_host = config.mongodb_conf[exchange]['host']

        # 构造数据库客户端对象
        db_client = MongoClient(target_host)

    return db_client


def get_target_collection(db_client, exchange):
    """
    获取目标集合对象
    :param db_client: 数据库客户端对象
    :param exchange: 与数据库关联的交易所名
    :return:
    """
    if exchange in config.mongodb_conf.keys():
        # 获取配置数据
        target_db = config.mongodb_conf[exchange]['db']
        target_collection = config.mongodb_conf[exchange]['collection']

        return db_client[target_db][target_collection]

    return None


def push_latest_quots(ws, target_collection):
    """
    获取数据库中的最新数据并推送至客户端
    :param ws: websocket实例
    :param target_collection: 目标数据库集合对象
    :return:
    """

    # 获取最新数据
    latest_quots = target_collection.find_one()

    if latest_quots:
        # 推送至客户端
        push_quots(ws, latest_quots)


def push_quots(ws, quots):
    """
    推送行情到客户端
    :param ws: websocket实例
    :param quots: 行情数据
    :return:
    """
    ws.send(bytes(json.dumps(utils.compact_quotations(quots)), "ascii"))


def watch_db_insert(ws, target_collection):
    """
    数据库插入监视，实现数据实时推送
    :param ws: websocket实例
    :param target_collection: 目标数据库集合对象
    :return:
    """
    # 缓冲区，临时存储新数据
    new_quots = []

    # 监视更新流,获取新插入的数据
    for inserted in target_collection.watch([{'$match': {'operationType': 'insert'}}]):
        # 回调事件处理器
        on_db_inserted(ws, inserted['fullDocument'], new_quots)


def on_db_inserted(ws, document, buffer):
    """
    事件处理器，当监测到插入操作时回调
    :param ws: websocket实例
    :param document: 新插入的文档
    :param buffer: 数据缓冲区
    :return:
    """
    if config.debug:
        print(document)

    if len(buffer) < config.quots_num_per_message:
        # 缓冲区不满时加入数据
        buffer.append(document)
    else:
        # 当缓冲增加至设定的长度，进行推送
        push_quots(ws, buffer)

        # 清空缓冲区
        buffer = []


def on_error(ws, db_client, error):
    """
    事件处理器，发生错误时回调
    :param ws: websocket实例
    :param db_client: 数据库客户端对象
    :param error: 错误信息
    :return:
    """
    # 关闭websocket和数据库
    try:
        ws.close()
        db_client.close()
    except Exception:
        pass

    print(error)
