from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "news_app"

    def ready(self):
        # Import signal handlers when Django starts.
        import news_app.signals  # noqa: F401