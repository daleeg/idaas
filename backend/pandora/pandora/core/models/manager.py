# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import logging
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.db.models.deletion import Collector
from django.utils.translation import ugettext_lazy as _
from mptt.managers import TreeManager
from mptt import utils
from mptt.exceptions import InvalidMove

__all__ = [
    "BaseSet",
    "BaseQuerySet",
    "BaseManager",
    "MpttTreeManager"
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

    @classmethod
    def message(cls):
        return ",".join(["{}:{}".format(key, vaule) for key, vaule in cls.MESSAGE.items()])


class BaseQuerySet(QuerySet):
    def delete(self, soft=True):

        """Delete the records in the current QuerySet."""
        assert self.query.can_filter(), \
            "Cannot use `limit` or `offset` with delete."

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
            for instance in del_query:
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
        lookup = kwargs
        params = self._extract_model_params(defaults, **kwargs)
        self._for_write = True
        with transaction.atomic(using=self.db):
            lookup["is_deleted"] = False
            objs = self.select_for_update().filter(**lookup)
            exist_obj = None
            for obj in objs:
                exist_obj = obj
            if not exist_obj:
                obj, created = self._create_object_from_params(lookup, params)
                if created:
                    return obj, created
            obj = exist_obj
            objs.exclude(pk=obj.pk).delete()
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


class BaseTreeQueryset(BaseQuerySet):
    def get_descendants(self, *args, **kwargs):
        """
        Alias to `mptt.managers.TreeManager.get_queryset_descendants`.
        """
        return self.model._tree_manager.get_queryset_descendants(self, *args, **kwargs)

    get_descendants.queryset_only = True

    def get_ancestors(self, *args, **kwargs):
        """
        Alias to `mptt.managers.TreeManager.get_queryset_ancestors`.
        """
        return self.model._tree_manager.get_queryset_ancestors(self, *args, **kwargs)

    get_ancestors.queryset_only = True

    def get_cached_trees(self):
        """
        Alias to `mptt.utils.get_cached_trees`.
        """
        return utils.get_cached_trees(self)


class BaseManager(models.Manager):
    """
    仅返回未被删除的实例
    """
    _queryset_class = BaseQuerySet

    def get_queryset(self):
        """
        在这里处理一下QuerySet, 然后返回没被标记位is_deleted的QuerySet
        """
        kwargs = {"model": self.model, "using": self._db}
        if hasattr(self, "_hints"):
            kwargs["hints"] = self._hints
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class MpttTreeManager(TreeManager):
    _queryset_class = BaseTreeQueryset

    def get_queryset(self):
        kwargs = {"model": self.model, "using": self._db}
        if hasattr(self, "_hints"):
            kwargs["hints"] = self._hints
        return self._queryset_class(**kwargs).filter(is_deleted=False).order_by(
            self.tree_id_attr, self.left_attr
        )

    def _inter_tree_move_and_close_gap(
            self, node, level_change,
            left_right_change, new_tree_id):
        """
        Removes ``node`` from its current tree, with the given set of
        changes being applied to ``node`` and its descendants, closing
        the gap left by moving ``node`` as it does so.
        """
        connection = self._get_connection(instance=node)
        qn = connection.ops.quote_name

        opts = self.model._meta
        inter_tree_move_query = """
        UPDATE %(table)s
        SET %(level)s = CASE
                WHEN %(left)s >= %%s AND %(left)s <= %%s
                    THEN %(level)s - %%s
                ELSE %(level)s END,
            %(tree_id)s = CASE
                WHEN %(left)s >= %%s AND %(left)s <= %%s
                    THEN %%s
                ELSE %(tree_id)s END,
            %(left)s = CASE
                WHEN %(left)s >= %%s AND %(left)s <= %%s
                    THEN %(left)s - %%s
                WHEN %(left)s > %%s
                    THEN %(left)s - %%s
                ELSE %(left)s END,
            %(right)s = CASE
                WHEN %(right)s >= %%s AND %(right)s <= %%s
                    THEN %(right)s - %%s
                WHEN %(right)s > %%s
                    THEN %(right)s - %%s
                ELSE %(right)s END
        WHERE %(tree_id)s = %%s AND is_deleted = 0""" % {
            "table": qn(self.tree_model._meta.db_table),
            "level": qn(opts.get_field(self.level_attr).column),
            "left": qn(opts.get_field(self.left_attr).column),
            "tree_id": qn(opts.get_field(self.tree_id_attr).column),
            "right": qn(opts.get_field(self.right_attr).column),
        }

        left = getattr(node, self.left_attr)
        right = getattr(node, self.right_attr)
        gap_size = right - left + 1
        gap_target_left = left - 1
        params = [
            left, right, level_change,
            left, right, new_tree_id,
            left, right, left_right_change,
            gap_target_left, gap_size,
            left, right, left_right_change,
            gap_target_left, gap_size,
            getattr(node, self.tree_id_attr)
        ]

        cursor = connection.cursor()
        cursor.execute(inter_tree_move_query, params)

    def _make_sibling_of_root_node(self, node, target, position):
        """
        Moves ``node``, making it a sibling of the given ``target`` root
        node as specified by ``position``.

        ``node`` will be modified to reflect its new tree state in the
        database.

        Since we use tree ids to reduce the number of rows affected by
        tree mangement during insertion and deletion, root nodes are not
        true siblings; thus, making an item a sibling of a root node is
        a special case which involves shuffling tree ids around.
        """
        if node == target:
            raise InvalidMove(_("A node may not be made a sibling of itself."))

        opts = self.model._meta
        tree_id = getattr(node, self.tree_id_attr)
        target_tree_id = getattr(target, self.tree_id_attr)

        if node.is_child_node():
            if position == "left":
                space_target = target_tree_id - 1
                new_tree_id = target_tree_id
            elif position == "right":
                space_target = target_tree_id
                new_tree_id = target_tree_id + 1
            else:
                raise ValueError(_("An invalid position was given: %s.") % position)

            self._create_tree_space(space_target)
            if tree_id > space_target:
                # The node"s tree id has been incremented in the
                # database - this change must be reflected in the node
                # object for the method call below to operate on the
                # correct tree.
                setattr(node, self.tree_id_attr, tree_id + 1)
            self._make_child_root_node(node, new_tree_id)
        else:
            if position == "left":
                if target_tree_id > tree_id:
                    left_sibling = target.get_previous_sibling()
                    if node == left_sibling:
                        return
                    new_tree_id = getattr(left_sibling, self.tree_id_attr)
                    lower_bound, upper_bound = tree_id, new_tree_id
                    shift = -1
                else:
                    new_tree_id = target_tree_id
                    lower_bound, upper_bound = new_tree_id, tree_id
                    shift = 1
            elif position == "right":
                if target_tree_id > tree_id:
                    new_tree_id = target_tree_id
                    lower_bound, upper_bound = tree_id, target_tree_id
                    shift = -1
                else:
                    right_sibling = target.get_next_sibling()
                    if node == right_sibling:
                        return
                    new_tree_id = getattr(right_sibling, self.tree_id_attr)
                    lower_bound, upper_bound = new_tree_id, tree_id
                    shift = 1
            else:
                raise ValueError(_("An invalid position was given: %s.") % position)

            connection = self._get_connection(instance=node)
            qn = connection.ops.quote_name

            root_sibling_query = """
            UPDATE %(table)s
            SET %(tree_id)s = CASE
                WHEN %(tree_id)s = %%s
                    THEN %%s
                ELSE %(tree_id)s + %%s END
            WHERE %(tree_id)s >= %%s AND %(tree_id)s <= %%s AND is_deleted = 0""" % {
                "table": qn(self.tree_model._meta.db_table),
                "tree_id": qn(opts.get_field(self.tree_id_attr).column),
            }

            cursor = connection.cursor()
            cursor.execute(root_sibling_query, [tree_id, new_tree_id, shift,
                                                lower_bound, upper_bound])
            setattr(node, self.tree_id_attr, new_tree_id)

    def _manage_space(self, size, target, tree_id):
        """
        Manages spaces in the tree identified by ``tree_id`` by changing
        the values of the left and right columns by ``size`` after the
        given ``target`` point.
        """
        if self.tree_model._mptt_is_tracking:
            self.tree_model._mptt_track_tree_modified(tree_id)
        else:
            connection = self._get_connection()
            qn = connection.ops.quote_name

            opts = self.model._meta
            space_query = """
            UPDATE %(table)s
            SET %(left)s = CASE
                    WHEN %(left)s > %%s
                        THEN %(left)s + %%s
                    ELSE %(left)s END,
                %(right)s = CASE
                    WHEN %(right)s > %%s
                        THEN %(right)s + %%s
                    ELSE %(right)s END
            WHERE %(tree_id)s = %%s AND is_deleted = 0
              AND (%(left)s > %%s OR %(right)s > %%s)""" % {
                "table": qn(self.tree_model._meta.db_table),
                "left": qn(opts.get_field(self.left_attr).column),
                "right": qn(opts.get_field(self.right_attr).column),
                "tree_id": qn(opts.get_field(self.tree_id_attr).column),
            }
            cursor = connection.cursor()
            cursor.execute(space_query, [target, size, target, size, tree_id,
                                         target, target])

    def _move_child_within_tree(self, node, target, position):
        """
        Moves child node ``node`` within its current tree relative to
        the given ``target`` node as specified by ``position``.

        ``node`` will be modified to reflect its new tree state in the
        database.
        """
        left = getattr(node, self.left_attr)
        right = getattr(node, self.right_attr)
        level = getattr(node, self.level_attr)
        width = right - left + 1
        tree_id = getattr(node, self.tree_id_attr)
        target_left = getattr(target, self.left_attr)
        target_right = getattr(target, self.right_attr)
        target_level = getattr(target, self.level_attr)

        if position == "last-child" or position == "first-child":
            if node == target:
                raise InvalidMove(_("A node may not be made a child of itself."))
            elif left < target_left < right:
                raise InvalidMove(_("A node may not be made a child of any of its descendants."))
            if position == "last-child":
                if target_right > right:
                    new_left = target_right - width
                    new_right = target_right - 1
                else:
                    new_left = target_right
                    new_right = target_right + width - 1
            else:
                if target_left > left:
                    new_left = target_left - width + 1
                    new_right = target_left
                else:
                    new_left = target_left + 1
                    new_right = target_left + width
            level_change = level - target_level - 1
            parent = target
        elif position == "left" or position == "right":
            if node == target:
                raise InvalidMove(_("A node may not be made a sibling of itself."))
            elif left < target_left < right:
                raise InvalidMove(_("A node may not be made a sibling of any of its descendants."))
            if position == "left":
                if target_left > left:
                    new_left = target_left - width
                    new_right = target_left - 1
                else:
                    new_left = target_left
                    new_right = target_left + width - 1
            else:
                if target_right > right:
                    new_left = target_right - width + 1
                    new_right = target_right
                else:
                    new_left = target_right + 1
                    new_right = target_right + width
            level_change = level - target_level
            parent = getattr(target, self.parent_attr)
        else:
            raise ValueError(_("An invalid position was given: %s.") % position)

        left_boundary = min(left, new_left)
        right_boundary = max(right, new_right)
        left_right_change = new_left - left
        gap_size = width
        if left_right_change > 0:
            gap_size = -gap_size

        connection = self._get_connection(instance=node)
        qn = connection.ops.quote_name

        opts = self.model._meta
        # The level update must come before the left update to keep
        # MySQL happy - left seems to refer to the updated value
        # immediately after its update has been specified in the query
        # with MySQL, but not with SQLite or Postgres.
        move_subtree_query = """
        UPDATE %(table)s
        SET %(level)s = CASE
                WHEN %(left)s >= %%s AND %(left)s <= %%s
                  THEN %(level)s - %%s
                ELSE %(level)s END,
            %(left)s = CASE
                WHEN %(left)s >= %%s AND %(left)s <= %%s
                  THEN %(left)s + %%s
                WHEN %(left)s >= %%s AND %(left)s <= %%s
                  THEN %(left)s + %%s
                ELSE %(left)s END,
            %(right)s = CASE
                WHEN %(right)s >= %%s AND %(right)s <= %%s
                  THEN %(right)s + %%s
                WHEN %(right)s >= %%s AND %(right)s <= %%s
                  THEN %(right)s + %%s
                ELSE %(right)s END
        WHERE %(tree_id)s = %%s AND is_deleted = 0""" % {
            "table": qn(self.tree_model._meta.db_table),
            "level": qn(opts.get_field(self.level_attr).column),
            "left": qn(opts.get_field(self.left_attr).column),
            "right": qn(opts.get_field(self.right_attr).column),
            "tree_id": qn(opts.get_field(self.tree_id_attr).column),
        }

        cursor = connection.cursor()
        cursor.execute(move_subtree_query, [
            left, right, level_change,
            left, right, left_right_change,
            left_boundary, right_boundary, gap_size,
            left, right, left_right_change,
            left_boundary, right_boundary, gap_size,
            tree_id])

        # Update the node to be consistent with the updated
        # tree in the database.
        setattr(node, self.left_attr, new_left)
        setattr(node, self.right_attr, new_right)
        setattr(node, self.level_attr, level - level_change)
        setattr(node, self.parent_attr, parent)
        node._mptt_cached_fields[self.parent_attr] = parent.pk
