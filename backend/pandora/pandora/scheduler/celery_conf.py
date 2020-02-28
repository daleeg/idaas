from __future__ import absolute_import, unicode_literals
from kombu import Queue, Exchange
import datetime
import os

redis_host = os.environ.get('REDIS_HOST', "127.0.0.1")
redis_port = os.environ.get('REDIS_PORT', 6379)
broker_url = 'redis://{}:{}/8'.format(redis_host, redis_port)
result_backend = 'redis://{}:{}/9'.format(redis_host, redis_port)

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

timezone = 'Asia/Shanghai'
enable_utc = True

include = ['pandora.scheduler.tasks']

result_expires = 3600

worker_concurrency = 2
worker_max_tasks_per_child = 5
worker_max_memory_per_child = 500000
# worker_pool = "gevent"
# beat_scheduler = SuperPersistentScheduler

disable_rate_limit = True

beat_schedule = {
}

task_queues = (
    Queue('celery', exchange=Exchange('celery'), routing_key='celery'),
    Queue('beat', exchange=Exchange('beat'), routing_key='beat'),
    Queue('sync', exchange=Exchange('sync'), routing_key='sync'),
)

task_routes = {

}
