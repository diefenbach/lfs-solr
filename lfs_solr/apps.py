from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'lfs_solr'

    def ready(self):
        import pdb; pdb.set_trace()
        import listeners  # NOQA
