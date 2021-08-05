# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from pandora.core.cachedependency import client


def reset_api_cache(stdout, keys):
    tables = client.mapping.get_dependent_items(keys)
    ret = client.refresh_all_cache_tables(tables)
    stdout.write("LEVEL_ALL: {}\n".format(ret[client.LEVEL_ALL]), ending="")


api_keys = client.mapping.api_keys
help_str = "reset all api cache : {}".format("             \n".join(api_keys))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--api",
            dest="api",
            action="store",
            help=help_str,
        )

    def handle(self, *args, **options):
        self.stdout.write("reset all api_cache start\n", ending="")

        try:
            key = options["api"]
            if key not in api_keys:
                raise CommandError("need right api")
            reset_api_cache(self.stdout, [key])
        except Exception as e:
            self.stdout.write("reset all api_cache failed\n", ending="")
            raise CommandError(e)
        self.stdout.write("reset all api_cache finish\n", ending="")
