from django.apps import AppConfig


class FriendsbookConfig(AppConfig):
    name = 'friendsbook'

    def ready(self):
        import friendsbook.signals
