import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.sites.models import Site
site = Site.objects.get_current()
print(f"Current Site ID: {site.id}")
print(f"Domain: {site.domain}")
print(f"Name: {site.name}")
