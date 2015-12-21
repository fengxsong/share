#-coding:utf-8-*-

import requests
import redis
import time
from celery import Celery

"""
usage:celery -A tasks worker --beat -l info
"""


app = Celery('tasks')
app.config_from_object('celeryconfig')
redis_host = app.conf['REDIS_HOST']
redis_port = app.conf['REDIS_PORT']
redis_db = app.conf['REDIS_DB']

JOBS = {
    'test': 'http://git.wljiashi.cn',
    'auto_returns': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_returns',
    'auto_allot_order_money': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_allot_order_money',
    'auto_confirm': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_confirm',
    'save_qq_record': 'http://www.wljiashi.com/api/tasks.php?act=save_qq_record',
    'mail_queue': 'http://www.wljiashi.com/api/tasks.php?app=mail_queue',
    'save_works_view_to_db': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=save_works_view_to_db',
    'auto_execute_activity': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_execute_activity',
    'auto_insert_customer': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_insert_customer',
    'save_goods_search_to_db': 'http://www.wljiashi.com/api/tasks.php?act=save_goods_search_to_db',
    'make_wl_return_detail_data': 'http://8.wljiashi.com/api/make_wl_return_detail_data.php?act=returns',
    'auto_cancel_order': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_cancel_order',
    'make_wl_order_day': 'http://8.wljiashi.com/api/make_wl_order_day.php?act=get_order_day',
    'save_goods_view_to_db': 'http://www.wljiashi.com/api/tasks.php?act=save_goods_view_to_db',
    'update_orders_clearing_status': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_update_orders_clearing_status',
    'save_news_view_to_db': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=save_news_view_to_db',
    'auto_evaluate': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_evaluate',
    'make_wl_day_detail_data': 'http://8.wljiashi.com/api/make_wl_day_detail_data.php?act=do',
    'auto_insert_order_clearing': 'http://www.wljiashi.com/api/tasks.php?app=tasks&act=auto_insert_order_clearing'
}

pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
r = redis.Redis(connection_pool=pool)
pipe = r.pipeline()


def pipe_hset(k, msg, fail=False):
    next_fail = int(r.hget(k, 'fails')) + 1 if fail else 0
    pipe.hset(k, 'timestamp', time.time()).hset(
        k, 'msg', msg).hset(k, 'fails', next_fail).execute()


@app.task
def run_crontab(slug, timeout=10):
    headers = {'User-Agent': 'celery_crontab_test_ua'}
    try:
        if not r.hgetall(slug):
            pipe_hset(slug, '200')
        url = JOBS[slug]
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            pipe_hset(slug, resp.status_code, fail=True)
        else:
            pipe_hset(slug, '200')

    except Exception as e:
        pipe_hset(slug, e, fail=True)
