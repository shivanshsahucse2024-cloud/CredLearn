import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_linkedin_app():
    # 1. Ensure Site exists
    site, created = Site.objects.get_or_create(id=1)
    site.domain = '127.0.0.1:8000'
    site.name = 'CredLearn'
    site.save()
    print(f"Site configured: {site.domain}")

    # 2. Create/Update SocialApp
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    provider = 'linkedin_oauth2'

    app, created = SocialApp.objects.get_or_create(
        provider=provider,
        defaults={
            'name': 'LinkedIn',
            'client_id': client_id,
            'secret': secret,
        }
    )
    
    if not created:
        app.client_id = client_id
        app.secret = secret
        app.save()
        print("Updated existing SocialApp")
    else:
        print("Created new SocialApp")

    # 3. Link Site to App
    app.sites.add(site)
    print("Linked App to Site")

if __name__ == "__main__":
    setup_linkedin_app()
