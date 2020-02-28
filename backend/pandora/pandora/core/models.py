#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel, ForeignObjectRel, OneToOneRel
from pandora.utils.constants import Message
from pandora.utils.queue import RedisQueue
from django.db.models.signals import post_save
from django.db.models.deletion import Collector
import pandora.utils.constants as cst
import logging
import uuid
import datetime

__all__ = [
    "CoreModel",
    "ExtraCoreModel",
    'BaseSet',
    'BaseQuerySet',
]

LOG = logging.getLogger(__name__)


class BaseSet(object):
    MESSAGE = {
    }

    @classmethod
    def choices(cls):
        return tuple(cls.MESSAGE.items())

    @classmethod
    def range(cls):
        return tuple(cls.MESSAGE.keys())

    @classmethod
    def check(cls, key):
        return key in cls.MESSAGE.keys()


class BaseQuerySet(QuerySet):
    def delete(self, soft=True):

        """Delete the records in the current QuerySet."""
        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."

        if self._fields is not None:
            raise TypeError("Cannot call delete() after .values() or .values_list()")

        del_query = self._chain()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        if not soft:
            collector = Collector(using=del_query.db)
            collector.collect(del_query)
            deleted, _rows_count = collector.delete()
        else:
            _rows_count = 0
            for instance in self.all():
                instance.delete(soft=True, using=del_query.db)
                _rows_count += 1

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
        return None, _rows_count

    def update_or_create(self, defaults=None, auto_delete_multi=True, **kwargs):
        """
        Look up an object with the given kwargs, updating one with defaults
        if it exists, otherwise create a new one.
        Return a tuple (object, created), where created is a boolean
        specifying whether an object was created.
        """
        if not auto_delete_multi:
            return super(BaseQuerySet, self).update_or_create(defaults, **kwargs)

        defaults = defaults or {}
        lookup, params = self._extract_model_params(defaults, **kwargs)
        self._for_write = True
        with transaction.atomic(using=self.db):
            lookup['is_deleted'] = False
            objs = self.select_for_update().filter(**lookup)
            exist_obj = None
            for obj in objs:
                exist_obj = obj
            if not exist_obj:
                obj, created = self._create_object_from_params(lookup, params)
                if created:
                    return obj, created
            obj = exist_obj
            objs.exclude(id=obj.id).delete()
            for k, v in defaults.items():
                setattr(obj, k, v() if callable(v) else v)
            obj.save(using=self.db)
        return obj, False

    def bulk_create(self, objs, _signal_post=0, batch_size=None):
        #  _signal_post: -1 all, 0 no, k  min(k, all)
        create_objs = super().bulk_create(objs, batch_size=batch_size)
        signal_count = 0
        if _signal_post:
            for obj in create_objs:
                signal_count += 1
                if 0 < _signal_post < signal_count:
                    break
                post_save.send(obj.__class__, instance=obj, created=True)
        return create_objs

    def update(self, _signal_post=0, **kwargs):
        #  _signal_post: -1 all, 0 no, k  min(k, all)
        if not _signal_post:
            return super().update(**kwargs)

        update_objects = []
        signal_count = 0
        for obj in self._chain():
            signal_count += 1
            if 0 < _signal_post < signal_count:
                break
            update_objects.append(obj)
        rows = super().update(**kwargs)
        for obj in update_objects:
            post_save.send(obj.__class__, instance=obj, created=False)
        return rows


class BaseManager(models.Manager):
    """
    仅返回未被删除的实例
    """
    _queryset_class = BaseQuerySet

    def get_queryset(self):
        """
        在这里处理一下QuerySet, 然后返回没被标记位is_deleted的QuerySet
        """
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class CoreModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_("唯一标识uid"), db_index=True)
    is_deleted = models.DateTimeField(null=True, default=False,
                                      help_text=_("表项的删除时间，为空标识未删除"))

    objects = BaseManager()
    async_fields = None
    async_queue = None
    is_cascade = False

    class Meta:
        abstract = True

    def get_async_fields(self):
        return [] if not self.async_fields else self.async_fields

    def get_async_queue(self):
        if not self.async_queue:
            self.async_queue = RedisQueue(cst.REPLICATION_TASK_QUEUE)
        return self.async_queue

    def delete(self, using=None, keep_parents=False, soft=True):
        """
        这里需要真删除的话soft=False即可
        """
        if soft:
            self.is_deleted = True
            self.save(update_fields=['is_deleted'], using=using)
            if self.is_cascade:
                LOG.info("delete instance: {}: {}".format(self.__class__.__name__, self.pk))
                cascade_chains = []
                related_update_fields = []
                async_message = False
                async_fields = self.get_async_fields()
                for local_field in self._meta.local_fields:
                    if local_field.name in async_fields:
                        async_message = True
                        continue
                    if isinstance(local_field, models.OneToOneField):
                        one2one = getattr(self, local_field.name)
                        if one2one:
                            setattr(self, local_field.name, None)
                            related_update_fields.append(local_field.name)
                            cascade_chains.append(one2one)
                            # one2one.is_deleted = True
                            # one2one.save(update_fields=['is_deleted'])
                    elif isinstance(local_field, models.ForeignKey):
                        if getattr(self, local_field.name):
                            setattr(self, local_field.name, None)
                            related_update_fields.append(local_field.name)
                            # self.save(using=using, update_fields=[local_field.name])
                if len(related_update_fields):
                    self.save(update_fields=related_update_fields, using=using)
                for related_object in self._meta.related_objects:
                    if related_object.name in async_fields:
                        async_message = True
                        continue

                    if related_object.related_name:
                        related_name = related_object.related_name
                    else:
                        related_name = '{}_set'.format(related_object.name)
                    if isinstance(related_object, OneToOneRel):
                        one2one = getattr(self, related_name, None)
                        if one2one:
                            if related_object.on_delete == models.CASCADE:
                                cascade_chains.append(one2one)
                            elif related_object.on_delete == models.SET_NULL:
                                setattr(self, related_name, None)

                    elif isinstance(related_object, ManyToOneRel):
                        many2one = getattr(self, related_name).all()
                        if many2one:
                            if related_object.on_delete == models.CASCADE:
                                cascade_chains.append(many2one)
                            elif related_object.on_delete == models.SET_NULL:
                                try:
                                    many2one.update(**{related_object.field.name: None})
                                except Exception as e:
                                    LOG.error(e)

                    elif isinstance(related_object, ManyToManyRel):
                        getattr(self, related_name).clear()
                for cascade in cascade_chains:
                    cascade.delete()

                if async_message:
                    msg = Message(code="{}".format(self.uid), action="delete", model=self.__class__.__name__, param={})
                    LOG.info(msg)
                    self.get_async_queue().enq(msg, lambda x: x._asdict())

        else:
            return super(CoreModel, self).delete(using=using, keep_parents=keep_parents)


class ExtraCoreModel(CoreModel):
    create_time = models.DateTimeField(help_text=_("创建时间, 2018-1-1T1:1:1.1111"), auto_now_add=True)
    update_time = models.DateTimeField(help_text=_("修改时间, 2018-1-1T1:1:1.1111"), auto_now=True)

    class Meta:
        abstract = True
