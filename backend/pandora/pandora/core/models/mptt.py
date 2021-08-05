#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import logging
from pandora.utils.snowflake import snow_flake
from django.db import models, router
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel, OneToOneRel
from mptt.compat import cached_field_value
from mptt.models import MPTTModel

from .manager import BaseManager, MpttTreeManager

__all__ = [
    "MpttCoreModel",
    "MpttExtraCoreModel",
]

LOG = logging.getLogger(__name__)


class MpttCoreModel(MPTTModel):
    uid = models.BigIntegerField(primary_key=True, default=snow_flake.get_id, help_text=_("唯一标识uid"))
    is_deleted = models.BooleanField(default=False, help_text=_("是否删除"))

    objects = MpttTreeManager()
    is_cascade = True

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, soft=True):
        """
        这里需要真删除的话soft=False即可
        """
        if soft:
            try:
                # We have to make sure we use database's mptt values, since they
                # could have changed between the moment the instance was retrieved and
                # the moment it is deleted.
                # This happens for example if you delete several nodes at once from a queryset.
                fields_to_refresh = [self._mptt_meta.right_attr,
                                     self._mptt_meta.left_attr,
                                     self._mptt_meta.tree_id_attr, ]
                self.refresh_from_db(fields=fields_to_refresh)
            except self.__class__.DoesNotExist as e:
                # In case the object was already deleted, we don't want to throw an exception
                pass
            tree_width = (self._mpttfield('right') -
                          self._mpttfield('left') + 1)
            target_right = self._mpttfield('right')
            tree_id = self._mpttfield('tree_id')
            self._tree_manager._close_gap(tree_width, target_right, tree_id)
            parent = cached_field_value(self, self._mptt_meta.parent_attr)

            if parent:
                right_shift = -self.get_descendant_count() - 2
                self._tree_manager._post_insert_update_cached_parent_right(parent, right_shift)

            self.is_deleted = True
            self._save(update_fields=["is_deleted"], using=using)

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
                    self._save(update_fields=related_update_fields, using=using)
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
            return super(MpttCoreModel, self).delete(using=using, keep_parents=keep_parents)

    def _save(self, force_insert=False, force_update=False, using=None,
              update_fields=None):
        for field in self._meta.concrete_fields:
            # If the related field isn't cached, then an instance hasn't
            # been assigned and there's no need to worry about this check.
            if field.is_relation and field.is_cached(self):
                obj = getattr(self, field.name, None)
                if not obj:
                    continue
                # A pk may have been assigned manually to a model instance not
                # saved to the database (or auto-generated in a case like
                # UUIDField), but we allow the save to proceed and rely on the
                # database to raise an IntegrityError if applicable. If
                # constraints aren't supported by the database, there's the
                # unavoidable risk of data corruption.
                if obj.pk is None:
                    # Remove the object from a related instance cache.
                    if not field.remote_field.multiple:
                        field.remote_field.delete_cached_value(obj)
                    raise ValueError(
                        "save() prohibited to prevent data loss due to "
                        "unsaved related object '%s'." % field.name
                    )
                elif getattr(self, field.attname) is None:
                    # Use pk from related object if it has been saved after
                    # an assignment.
                    setattr(self, field.attname, obj.pk)
                # If the relationship's pk/to_field was changed, clear the
                # cached relationship.
                if getattr(obj, field.target_field.attname) != getattr(self, field.attname):
                    field.delete_cached_value(self)

        using = using or router.db_for_write(self.__class__, instance=self)
        if force_insert and (force_update or update_fields):
            raise ValueError("Cannot force both insert and updating in model saving.")

        deferred_fields = self.get_deferred_fields()
        if update_fields is not None:
            # If update_fields is empty, skip the save. We do also check for
            # no-op saves later on for inheritance cases. This bailout is
            # still needed for skipping signal sending.
            if not update_fields:
                return

            update_fields = frozenset(update_fields)
            field_names = set()

            for field in self._meta.fields:
                if not field.primary_key:
                    field_names.add(field.name)

                    if field.name != field.attname:
                        field_names.add(field.attname)

            non_model_fields = update_fields.difference(field_names)

            if non_model_fields:
                raise ValueError("The following fields do not exist in this "
                                 "model or are m2m fields: %s"
                                 % ', '.join(non_model_fields))

        # If saving to the same database, and this model is deferred, then
        # automatically do an "update_fields" save on the loaded fields.
        elif not force_insert and deferred_fields and using == self._state.db:
            field_names = set()
            for field in self._meta.concrete_fields:
                if not field.primary_key and not hasattr(field, 'through'):
                    field_names.add(field.attname)
            loaded_fields = field_names.difference(deferred_fields)
            if loaded_fields:
                update_fields = frozenset(loaded_fields)

        self.save_base(using=using, force_insert=force_insert,
                       force_update=force_update, update_fields=update_fields)

    _save.alters_data = True


class MpttExtraCoreModel(MpttCoreModel):
    create_time = models.DateTimeField(help_text=_("创建时间, 2018-1-1T1:1:1.1111"), auto_now_add=True)
    update_time = models.DateTimeField(help_text=_("修改时间, 2018-1-1T1:1:1.1111"), auto_now=True)

    class Meta:
        abstract = True
