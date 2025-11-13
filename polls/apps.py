from django.apps import AppConfig

class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
    
    def ready(self):
        # This imports and registers the signals
        import polls.signals