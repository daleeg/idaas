# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management.base import CommandError
from django.core.management.commands import migrate
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, connections, models, router, transaction
from django.core.cache import caches
from django.core.cache.backends.db import BaseDatabaseCache
from django.db.utils import DatabaseError

plan_cache = {}
sync_plan_cache = {}


def reset_api_cache(stdout):
    from pandora.core.cachedependency import client
    stdout.write("reset all api_cache start\n", ending="")
    tables = client.mapping.get_dependent_items()
    ret = client.refresh_all_cache_tables(tables)
    stdout.write("LEVEL_COMPANY: {}\n".format(ret[client.LEVEL_COMPANY]), ending="")
    stdout.write("LEVEL_ALL: {}\n".format(ret[client.LEVEL_ALL]), ending="")
    stdout.write("LEVEL_COMPANY_SN: {}\n".format(ret[client.LEVEL_COMPANY_SN]), ending="")
    stdout.write("reset all api_cache stop\n", ending="")


def reset_lru_cache(stdout):
    from pandora.utils.fileutils import get_version_from_file
    stdout.write("reset lru_cache start\n", ending="")
    get_version_from_file.cache_clear()
    stdout.write("reset lru_cache stop\n", ending="")


@receiver(post_migrate)
def auto_future_operations_async(sender, app_config, verbosity, interactive, using, apps, plan, *args, **kwargs):
    # 异步处理升级原有旧数据
    messages_map = {}
    for mig, _ in plan:
        if mig.name in plan_cache:
            continue
        print(mig)
        plan_cache[mig.name] = mig
        future_operations = getattr(mig, "future_operations", [])
        for operation in future_operations:
            model = operation[0]
            action = operation[1]
            messages_map.setdefault(action, []).append(model)
    # queue = RedisQueue(queue=cst.UPGRADE_MODELS_QUEUE)
    # timestamp = timezone.now().timestamp()
    # for key, value in messages_map.items():
    #     msg = cst.UpgradeMessage(action=key, models=value, param={"timestamp": timestamp})
    #     queue.enq(msg._asdict())


@receiver(post_migrate)
def auto_current_operations_sync(sender, app_config, verbosity, interactive, using, apps, plan, *args, **kwargs):
    # 同步处理升级原有旧数据
    messages_map = {}
    for mig, _ in plan:
        if mig.name in sync_plan_cache:
            continue
        print(mig)
        sync_plan_cache[mig.name] = mig
        current_operations = getattr(mig, "current_operations", [])
        for operation in current_operations:
            model = operation[0]
            action = operation[1]
            messages_map.setdefault(action, []).append(model)
    # timestamp = timezone.now().timestamp()
    # for key, value in messages_map.items():
    #     upgrade_server(action=key, models=value, timestamp=timestamp)


def check_and_create_db_caches(stdout):
    database = DEFAULT_DB_ALIAS
    for cache_alias in settings.CACHES:
        cache = caches[cache_alias]
        if isinstance(cache, BaseDatabaseCache):
            create_db_cache_table(database, cache._table, stdout)


def create_db_cache_table(database, tablename, stdout):
    cache = BaseDatabaseCache(tablename, {})
    if not router.allow_migrate_model(database, cache.cache_model_class):
        return
    connection = connections[database]

    if tablename in connection.introspection.table_names():
        stdout.write("Cache table '%s' already exists." % tablename)
        return

    fields = (
        # "key" is a reserved word in MySQL, so use "cache_key" instead.
        models.CharField(name='cache_key', max_length=255, unique=True, primary_key=True),
        models.TextField(name='value'),
        models.DateTimeField(name='expires', db_index=True),
    )
    table_output = []
    index_output = []
    qn = connection.ops.quote_name
    for f in fields:
        field_output = [
            qn(f.name),
            f.db_type(connection=connection),
            '%sNULL' % ('NOT ' if not f.null else ''),
        ]
        if f.primary_key:
            field_output.append("PRIMARY KEY")
        elif f.unique:
            field_output.append("UNIQUE")
        if f.db_index:
            unique = "UNIQUE " if f.unique else ""
            index_output.append(
                "CREATE %sINDEX %s ON %s (%s);" %
                (unique, qn('%s_%s' % (tablename, f.name)), qn(tablename), qn(f.name))
            )
        table_output.append(" ".join(field_output))
    full_statement = ["CREATE TABLE %s (" % qn(tablename)]
    for i, line in enumerate(table_output):
        full_statement.append('    %s%s' % (line, ',' if i < len(table_output) - 1 else ''))
    full_statement.append(');')

    full_statement = "\n".join(full_statement)

    with transaction.atomic(using=database, savepoint=connection.features.can_rollback_ddl):
        with connection.cursor() as curs:
            try:
                curs.execute(full_statement)
            except DatabaseError as e:
                raise CommandError(
                    "Cache table '%s' could not be created.\nThe error was: %s." %
                    (tablename, e))
            for statement in index_output:
                curs.execute(statement)

    stdout.write("Cache table '%s' created." % tablename)


def pandora_pre_upgrade(stdout):
    reset_lru_cache(stdout)


def pandora_upgrade(stdout, reset_api=False):
    if reset_api:
        reset_api_cache(stdout)
    check_and_create_db_caches(stdout)


class Command(migrate.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--reset_api",
            action="store_true",
            dest="reset_api",
            help="reset all api cache",
            default=False,
        )

    def handle(self, *args, **options):
        self.stdout.write("upgrade start\n", ending="")
        try:
            pandora_pre_upgrade(self.stdout)
        except Exception as e:
            self.stdout.write("pre upgrade failed, {}\n".format(e), ending="")

        super(Command, self).handle(*args, **options)

        try:
            reset_api = options["reset_api"]
            pandora_upgrade(self.stdout, reset_api)
        except Exception as e:
            self.stdout.write("upgrade failed\n", ending="")
            raise CommandError(e)
        self.stdout.write("upgrade finish\n", ending="")
