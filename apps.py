from core.plugin_app_config import PluginAppConfig


class PatientEmailPluginConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.patient_email_plugin"
    verbose_name = "Patient Email Plugin"

    def ready(self):
        """Called when the app is ready."""
        super().ready()
        # Import the model extensions to register them
        # Import template hooks to register them
