from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from pandora.scheduler.celery_app import capp
from celery.utils.nodenames import node_format, host_format, default_nodename
from celery.utils.log import mlevel
# from celery import maybe_patch_concurrency


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--logfile", action="store", dest="logfile",
            default="/var/log/classboard/pandora/pandora_worker.log",
            help="logfile path",
        )

    def run_worker(self, hostname=None, loglevel="INFO", logfile=None, pidfile=None, statedb=None):
        pool_cls = capp.conf.worker_pool
        self.stdout.write("task_default_queue pool: {}\n".format(capp.conf.task_default_queue))
        self.stdout.write("work pool: {}\n".format(pool_cls))

        hostname = host_format(default_nodename(hostname))
        if loglevel:
            try:
                loglevel = mlevel(loglevel)
            except KeyError:  # pragma: no cover
                raise CommandError("Unknown level {0!r} ".format(
                    loglevel, ))
        self.stdout.write("hostname: {}\n".format(hostname))

        # maybe_patch_concurrency(argv=["-P", capp.conf.worker_pool])
        worker = capp.Worker(
            hostname=hostname, pool_cls=pool_cls, loglevel=loglevel,
            logfile=logfile,  # node format handled by celery.app.log.setup
            pidfile=node_format(pidfile, hostname),
            statedb=node_format(statedb, hostname),
        )
        worker.start()
        return worker.exitcode

    def handle(self, *args, **options):
        self.stdout.write("celery worker start\n", ending="")
        try:
            logfile = options["logfile"]
            self.run_worker(logfile=logfile)
        except Exception as e:
            self.stdout.write("celery worker failed\n", ending="")
            raise CommandError(e)
        self.stdout.write("celery worker finish\n", ending="")
