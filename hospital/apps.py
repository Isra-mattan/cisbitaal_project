import os
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_superuser(sender, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    username = 'admin'
    password = 'adminpassword123'
    email = 'admin@example.com'

    # Check if the user already exists to avoid errors on subsequent migrations
    if not User.objects.filter(username=username).exists():
        print(f"Abuurista superuser cusub: {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser si guul leh ayaa loo abuuray.")

class HospitalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital'

    def ready(self):
        # Waxaan ku xireynaa signal-ka post_migrate si markii migration-ka uu dhamaado loo waco create_superuser
        post_migrate.connect(create_superuser, sender=self)
