# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from pandora.scheduler.celery_app import capp
from celery.platforms import detached


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--logfile", action="store", dest="logfile",
            default="/var/log/classboard/pandora/pandora_beat.log",
            help="logfile path",
        )
        parser.add_argument(
            "-d",
            "--detached",
            action="store_true",
            dest="detached",
            help="is detached",
            default=False,
        )

    def run_beat(self, logfile=None, is_detached=False, max_interval=300):
        if not is_detached:
            capp.Beat(max_interval=max_interval, loglevel="INFO",
                      logfile="/var/log/classboard/pandora/pandora_beat.log").run()
        else:
            with detached(logfile):
                capp.Beat(max_interval=max_interval, loglevel="INFO",
                          logfile="/var/log/classboard/pandora/pandora_beat.log").run()

    def handle(self, *args, **options):
        self.stdout.write("celery cmd start\n", ending="")
        try:
            logfile = options["logfile"]
            is_detached = options["detached"]
            self.run_beat(logfile=logfile, is_detached=is_detached)
        except Exception as e:
            self.stdout.write("celery cmd failed\n", ending="")
            raise CommandError(e)
        self.stdout.write("celery cmd finish\n", ending="")
