import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from allauth.socialaccount.models import SocialAccount

print("Checking Social Accounts...")
for sa in SocialAccount.objects.filter(provider='linkedin'):
    print(f"User: {sa.user.username}")
    print(f"UID: {sa.uid}")
    print(f"Date Joined: {sa.date_joined}")
    print("Extra Data Keys:", list(sa.extra_data.keys()))
    print("Extra Data:", json.dumps(sa.extra_data, indent=2))
    print("-" * 20)
