from rest_framework.schemas import AutoSchema
from rest_framework.compat import coreschema
import coreapi
from collections import OrderedDict

STRING = coreschema.String
NUMBER = coreschema.Number
BOOL = coreschema.Boolean
ANY = coreschema.Anything
ARRAY = coreschema.Array
ENUM = coreschema.Enum
INTEGER = coreschema.Integer
UNION = coreschema.Union
OBJECT = coreschema.Object
QUERY = "query"
FORM = "form"
BODY = "body"
PATH = "path"
HEADER = "header"
ManualField = coreapi.Field


class ManualField(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ManualViewSchema(AutoSchema):
    def __init__(self, **kwargs):
        """
        Parameters:

        * `manual_fields`: list of `coreapi.Field` instances that
            will be added to auto-generated fields, overwriting on `Field.name`
        """
        self._manual_kwargs = kwargs
        super(ManualViewSchema, self).__init__()

    def get_manual_fields(self, path, method):
        action = getattr(self.view, 'action', None)
        extra = getattr(self.view, 'extra_manual_schema', {})

        manual_fields = self._manual_kwargs.get(method.lower(), []) + extra.get(method.lower(), [])
        if action:
            manual_fields += self._manual_kwargs.get(action, [])

        manual_fields += self._manual_kwargs.get("all", [])

        manual_fields = {field.name: field for field in manual_fields if hasattr(field, "name")}.values()

        return [
            coreapi.Field(
                name=field.name,
                required=field.__dict__.get("required", False),
                location=field.__dict__.get("location", QUERY if method.lower() in ["get", ] else FORM),
                schema=field.__dict__.get("schema", STRING()),
                description=field.__dict__.get("description", None),
                example=field.__dict__.get("example", None)
            ) for field in manual_fields if hasattr(field, "name")
        ]

    def _allows_filters(self, path, method):
        if getattr(self.view, 'filter_backends', None) is None:
            return False

        if hasattr(self.view, 'action'):
            return self.view.action in ["list", "batch_destroy", ]

        return method.lower() in ["get", "delete"]

    @staticmethod
    def update_fields(fields, update_with):
        """
        Update list of coreapi.Field instances, overwriting on `Field.name`.

        Utility function to handle replacing coreapi.Field fields
        from a list by name. Used to handle `manual_fields`.

        Parameters:

        * `fields`: list of `coreapi.Field` instances to update
        * `update_with: list of `coreapi.Field` instances to add or replace.
        """
        if not update_with:
            return fields

        by_name = OrderedDict(((f.name, f.location), f) for f in fields)
        for f in update_with:
            by_name[(f.name, f.location)] = f
        fields = list(by_name.values())
        return fields
