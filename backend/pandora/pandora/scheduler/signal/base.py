from __future__ import absolute_import, unicode_literals

from celery.signals import (before_task_publish,
                            after_task_publish,
                            task_retry,
                            task_success,
                            task_failure,
                            task_revoked, )

import logging

LOG = logging.getLogger(__name__)


@before_task_publish.connect
def before_task_sent_handler(sender=None, headers=None, body=None, routing_key=None, **kwargs):
    info = headers if 'task' in headers else body
    LOG.info('before_task_publish for task {info[id]} routing_key {rk}'.format(info=info, rk=routing_key))


@after_task_publish.connect
def after_task_sent_handler(sender=None, headers=None, body=None, routing_key=None, **kwargs):
    info = headers if 'task' in headers else body
    LOG.info('after_task_publish for task {info[id]} routing_key {rk}'.format(info=info, rk=routing_key))


@task_retry.connect
def retry_task_handler(sender=None, request=None, reason=None, einfo=None, **kwargs):
    LOG.info('retry_task {}----{}'.format(sender, reason))


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    LOG.info("success_task: {}----{}".format(sender, result))


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    LOG.info("failed_task: {}----{} {}".format(sender, task_id, exception))


@task_revoked.connect
def task_revoked_handler(sender=None, request=None, terminated=None, signum=None, expired=None, **kwargs):
    LOG.info("revoked_task: {} ---- {} ---- {}".format(terminated, signum, expired))
