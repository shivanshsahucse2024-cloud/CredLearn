import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser', 'test@example.com', 'password123')
    print("Test user created.")
else:
    print("Test user already exists.")
