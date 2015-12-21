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
    'test': 'http://some-url',
    'auto_returns': 'http://some-url',
    'auto_allot_order_money': 'http://some-url',
    'auto_confirm': 'http://some-url',
    'save_qq_record': 'http://some-url',
    'mail_queue': 'http://some-url',
    'save_works_view_to_db': 'http://some-url',
    'auto_execute_activity': 'http://some-url',
    'auto_insert_customer': 'http://some-url',
    'save_goods_search_to_db': 'http://some-url',
    'make_wl_return_detail_data': 'http://some-url',
    'auto_cancel_order': 'http://some-url',
    'make_wl_order_day': 'http://some-url',
    'save_goods_view_to_db': 'http://some-url',
    'update_orders_clearing_status': 'http://some-url',
    'save_news_view_to_db': 'http://some-url',
    'auto_evaluate': 'http://some-url',
    'make_wl_day_detail_data': 'http://some-url',
    'auto_insert_order_clearing': 'http://some-url',
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
