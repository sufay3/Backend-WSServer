"""
功能函数集
"""


def compact_quotations(raw_quots):
    """
    精简行情数据格式
    :param raw_quots: 初始数据
    :return: 新格式数据
    """
    compact_quots = []

    # 如果参数是列表形式，即多条数据的情形
    if isinstance(raw_quots, list):
        for q in raw_quots:
            compact_quot = compact_quotation(q)
            compact_quots.append(compact_quot)

    # 单数据情形
    else:
        compact_quots.append(compact_quotation(raw_quots))

    return compact_quots


def compact_quotation(raw_quot):
    """
    精简单数据形式的行情格式
    :param raw_quot: 初始数据
    :return: 新格式数据
    """
    compact_quot = {}

    compact_quot['s'] = raw_quot['symbol']
    compact_quot['m'] = raw_quot['market']
    compact_quot['p'] = raw_quot['price']
    compact_quot['u'] = raw_quot['usd']
    compact_quot['c'] = raw_quot['cny']
    compact_quot['r'] = raw_quot['rate']
    compact_quot['h'] = raw_quot['high']
    compact_quot['l'] = raw_quot['low']
    compact_quot['v'] = raw_quot['vol']

    return compact_quot


def get_exchange(request):
    """
    从客户端请求中提取交易所名字
    :param request: 请求
    :return: 字符串，交易所名字或空
    """
    try:
        return request.GET['ex']
    except KeyError:
        return ''
