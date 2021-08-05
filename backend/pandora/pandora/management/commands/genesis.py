# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import UniqueTogetherValidator
from pandora import models
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "init.json")


class Genesis(object):
    def __init__(self):
        self.company_name = None

    def create(self, serializer_class, data):
        with transaction.atomic():
            serializer = serializer_class(data=data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                except Exception as e:
                    print(e)
                    raise CommandError(e)
            else:
                raise CommandError(serializer.errors)

    def get_tasks(self):
        with open(CONFIG_FILE, "r", encoding="utf-8_sig") as f:
            tasks = json.load(f)
        return tasks

    def load_items(self, _file):
        items = []
        with open(_file, "r", encoding="utf-8_sig") as f:
            lines = f.readlines()
            if len(lines) < 2:
                return items
            head = lines[0].strip().split(",")
            bodies = lines[1:]
            items_count = len(head)
            for body in bodies:
                data = body.strip().split(",")
                if len(data) != items_count:
                    print("error data format[{}]: {}".format(_file, data))
                    continue
                item = {}
                for i in range(items_count):
                    key = head[:][i].strip()
                    value = data[i].strip()
                    keys = key.split("__")
                    if len(keys) == 2:
                        model = getattr(models, keys[0].title(), None)
                        if not model:
                            continue
                        key = "{}_id".format(keys[0])
                        value = model.objects.get(**{keys[1]: value}).uid

                    item[key] = value

                items.append(item)
        return items

    COMPANY_NAME = None

    def process_task(self, path, model_str, unique_fields):
        full_path = os.path.join(os.path.dirname(__file__), "data", path)
        if not os.path.isfile(full_path):
            print("no file:{}".format(full_path))
            return
        items = self.load_items(full_path)
        task_model = getattr(models, model_str, None)
        if not task_model:
            print("no model:{}".format(model_str))
            return

        class InnerSerializer(ModelSerializer):
            class Meta:
                model = task_model
        if unique_fields:
            InnerSerializer.Meta.validators = [UniqueTogetherValidator(task_model.objects.all(), unique_fields)]

        for item in items:
            try:
                self.create(InnerSerializer, item)
                print("item success: {}".format(item))
            except:
                print("item failed: {}".format(item))

    def genesis_pandora(self):
        tasks = self.get_tasks()
        for task in tasks:
            if "path" in task and "model" in task:
                self.process_task(task["path"], task["model"], task.get("unique_fields", []))
            else:
                print("error task:{}".format(task))


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("genesis start\n", ending="")

        try:
            Genesis().genesis_pandora()
        except:
            self.stdout.write("genesis failed\n", ending="")
            raise
        self.stdout.write("genesis finish\n", ending="")
