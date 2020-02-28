import django.dispatch

app_broad = django.dispatch.Signal(providing_args=["instance", "id", "kind", "action", "extra", "group", "member"],
                                   use_caching=True)
