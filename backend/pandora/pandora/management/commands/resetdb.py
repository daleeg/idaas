# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import MySQLdb


def reset_db():
    db_info = settings.DATABASES["default"]
    db = MySQLdb.connect(host=db_info["HOST"], user=db_info["USER"], passwd=db_info["PASSWORD"],
                         port=db_info["PORT"], charset="utf8")
    cursor = db.cursor()
    # Below line  is hide your warning
    cursor.execute("SET sql_notes = 0; ")
    cursor.execute("drop database IF exists {}".format(db_info["NAME"]))
    cursor.execute("create database {} character set utf8 default collate utf8_general_ci".format(db_info["NAME"]))
    cursor.execute("SET sql_notes = 1; ")
    cursor.close()
    db.close()


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("reset db start\n", ending='')
        try:
            reset_db()
        except Exception as e:
            self.stdout.write("reset db failed\n", ending='')
            raise CommandError(e)
        self.stdout.write("reset db finish\n", ending='')
