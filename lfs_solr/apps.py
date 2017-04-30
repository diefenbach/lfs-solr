from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'lfs_solr'

    def ready(self):
        import listeners  # NOQA
