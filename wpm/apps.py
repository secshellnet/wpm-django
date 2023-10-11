from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WpmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wpm"
    verbose_name = _("wpm")

    def ready(self):
        from wpm.services.check_valid import check_valid
        import wpm.signals

        scheduler = BackgroundScheduler()
        scheduler.add_job(check_valid, 'interval', seconds=5)
        scheduler.start()
