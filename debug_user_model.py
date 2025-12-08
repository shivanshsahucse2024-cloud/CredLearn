import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

User = get_user_model()
print(f"Current User Model: {User}")
print(f"User DB Table: {User._meta.db_table}")

# Check SocialAccount relation
sa_field = SocialAccount._meta.get_field('user')
print(f"SocialAccount.user points to: {sa_field.related_model}")
print(f"SocialAccount.user target table: {sa_field.related_model._meta.db_table}")
