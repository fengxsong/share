#-*-coding:utf-8-*-

from celery.schedules import crontab
from datetime import timedelta

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 10

BROKER_URL = 'redis://%s:%d' % (REDIS_HOST, REDIS_PORT)
CELERY_RESULT_BACKEND = 'redis'


CELERYBEAT_SCHEDULE = {
    'test': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(),
        'args': ('test',),
    },

    'auto_returns': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': ('auto_returns',),
    },

    'auto_confirm': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/30'),
        'args': ('auto_confirm',),
    },

    'auto_allot_order_money': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/10'),
        'args': ('auto_allot_order_money',),
    },

    'auto_cancel_order': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/15'),
        'args': ('auto_cancel_order',),
    },

    'mail_queue': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/2'),
        'args': ('mail_queue',),
    },

    'make_wl_return_detail_data': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/20', hour='2,3,4'),
        'args': ('make_wl_return_detail_data',),
    },

    'make_wl_day_detail_data': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/10', hour='2,3,4'),
        'args': ('make_wl_day_detail_data',),
    },

    'auto_insert_customer': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/5', hour='2,3,4'),
        'args': ('auto_insert_customer',),
    },

    'auto_insert_order_clearing': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/5', hour='2,3,4'),
        'args': ('auto_insert_order_clearing',),
    },

    'make_wl_order_day': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=30, hour=4),
        'args': ('make_wl_order_day',),
    },

    'auto_evaluate': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=30, hour=3),
        'args': ('auto_evaluate',),
    },

    'update_orders_clearing_status': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute='*/10', hour='0,1', day_of_month='10'),
        'args': ('update_orders_clearing_status',),
    },

    'auto_execute_activity': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=0),
        'args': ('auto_execute_activity',),
    },

    'save_goods_view_to_db': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=0, hour=8),
        'args': ('save_goods_view_to_db',),
    },

    'save_goods_search_to_db': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=0, hour=7),
        'args': ('save_goods_search_to_db',),
    },

    'save_works_view_to_db': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=30, hour=7),
        'args': ('save_works_view_to_db',),
    },

    'save_qq_record': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=0, hour=6),
        'args': ('save_qq_record',),
    },

    'save_news_view_to_db': {
        'task': 'tasks.run_crontab',
        'schedule': crontab(minute=0, hour=4),
        'args': ('save_news_view_to_db',),
    },
}
