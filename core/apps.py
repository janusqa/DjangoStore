from django.apps import AppConfig


class coreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        import core.signals.handlers
