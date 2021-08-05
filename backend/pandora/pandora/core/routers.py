from rest_framework import routers
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


class APIRouter(routers.DefaultRouter):
    routes = [
        # List create route.
        routers.Route(
            url=r'{prefix}{trailing_slash}',
            mapping={
                'get': 'list',
                'post': 'create',
            },
            name='{basename}-list-process',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # bulk_create, bulk_delete route.

        routers.Route(
            url=r'{prefix}{trailing_slash}bulkcreate/',
            mapping={
                'post': 'bulk_create',

            },
            name='{basename}-bulk-create',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),

        routers.Route(
            url=r'{prefix}{trailing_slash}bulkdestroy/',
            mapping={
                'post': 'bulk_destroy',
            },
            name='{basename}-bulk-create',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),

        # Detail Update Delete route.
        routers.Route(
            url=r'{prefix}/{lookup}{trailing_slash}',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),

        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        routers.DynamicRoute(
            url=r'{prefix}/{url_path}{trailing_slash}',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        routers.DynamicRoute(
            url=r'{prefix}/{lookup}/{url_path}{trailing_slash}',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]

    def get_default_basename(self, viewset):
        """
        If `base_name` is not specified, attempt to automatically determine
        it from the endpoints.
        """

        base_name = getattr(viewset, 'base_name', None)
        if not base_name:
            base_name = super(APIRouter, self).get_default_basename(viewset)
        return base_name

    def registers(self, prefix, viewsets, base_name=None):
        for viewset in viewsets:
            self.register(prefix, viewset, base_name)

    def get_lookup_route(self, viewset, lookup_prefix=''):
        base_route = '<{lookup_type}:{lookup_prefix}{lookup_url_kwarg}>'
        # Use `pk` as default field, unset set.  Default regex should not
        # consume `.json` style suffixes and should break at '/' boundaries.
        lookup_field = getattr(viewset, 'lookup_field', 'uid')
        lookup_url_kwarg = getattr(viewset, 'lookup_url_kwarg', None) or lookup_field
        lookup_type = getattr(viewset, 'lookup_type', 'int')
        return base_route.format(
            lookup_type=lookup_type,
            lookup_prefix=lookup_prefix,
            lookup_url_kwarg=lookup_url_kwarg,
        )

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        urls = []
        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_route(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                # If there is no prefix, the first part of the url is probably
                #   controlled by project's urls.py and the router is in an app,
                #   so a slash in the beginning will (A) cause Django to give
                #   warnings and (B) generate URLS that will require using '//'.
                # if not prefix and regex[:2] == '^/':
                #     regex = '^' + regex[2:]

                initkwargs = route.initkwargs.copy()
                initkwargs.update({
                    'basename': basename,
                    'detail': route.detail,
                })

                view = viewset.as_view(mapping, **initkwargs)
                name = route.name.format(basename=basename)

                urls.append(path(regex, view, name=name))

        if self.include_root_view:
            view = self.get_api_root_view(api_urls=urls)
            root_url = path('', view, name=self.root_view_name)
            urls.append(root_url)

        # if self.include_format_suffixes:
        #     urls = format_suffix_patterns(urls)

        return urls
