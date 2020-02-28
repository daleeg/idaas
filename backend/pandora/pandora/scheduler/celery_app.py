from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms

platforms.C_FORCE_ROOT = True

os.environ.setdefault('CELERY_CONFIG_MODULE', 'pandora.scheduler.celery_conf')

capp = Celery("pandora")
capp.config_from_envvar('CELERY_CONFIG_MODULE')

# capp.conf.humanize(with_defaults=False, censored=True)
# capp.config_from_object('ct.conf')
# capp.autodiscover_tasks(packages=["pandora.scheduler"])

if __name__ == '__main__':
    print(capp.main)
    capp.worker_main()
