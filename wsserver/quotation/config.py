"""
行情服务器配置
"""

# MongoDB配置
mongodb_conf = {'binance': {'host': '127.0.0.1:27017', 'db': 'liansea', 'collection': 'quotation_binance'}}

# 控制每个推送消息中所包含的行情数
quots_num_per_message = 30

# 调试模式
debug = True

# 行情url
quot_url = r'ws/quots'
