import django.dispatch

message_channel = django.dispatch.Signal(providing_args=["instance", "table", "event"], use_caching=True)
