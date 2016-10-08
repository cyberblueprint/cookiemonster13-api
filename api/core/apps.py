from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'api.core'
    verbose_name = "Home"

    def ready(self):
        pass
