#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel, OneToOneRel
from .manager import BaseManager
from pandora.utils.snowflake import snow_flake

__all__ = [
    "CoreModel",
    "ExtraCoreModel",
]

LOG = logging.getLogger(__name__)


class CoreModel(models.Model):
    uid = models.BigIntegerField(primary_key=True, default=snow_flake.get_id, help_text=_("唯一标识uid"))
    is_deleted = models.BooleanField(default=False, help_text=_("是否删除"))

    objects = BaseManager()
    is_cascade = True

    class Meta:
        abstract = True

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
                for local_field in self._meta.local_fields:
                    if isinstance(local_field, models.OneToOneField):
                        one2one = getattr(self, local_field.name)
                        if one2one:
                            if not ("_ptr" in local_field.name and local_field.primary_key):
                                setattr(self, local_field.name, None)
                                related_update_fields.append(local_field.name)
                            # cascade_chains.append(one2one)
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

        else:
            return super(CoreModel, self).delete(using=using, keep_parents=keep_parents)

    @property
    def as_dict(self):
        result = {}
        for field in self._meta.local_fields:
            result[field.name] = getattr(self, field.name)
        return result


class ExtraCoreModel(CoreModel):
    create_time = models.DateTimeField(help_text=_("创建时间, 2018-1-1T1:1:1.1111"), auto_now_add=True)
    update_time = models.DateTimeField(help_text=_("修改时间, 2018-1-1T1:1:1.1111"), auto_now=True)

    class Meta:
        abstract = True
