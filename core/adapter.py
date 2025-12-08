from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import generate_unique_username
from django.utils.text import slugify
import logging
import traceback

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Hook that privileges the 'first_name' and 'last_name' over the email
        for the username generation.
        """
        user = super().populate_user(request, sociallogin, data)
        
        first_name = data.get('first_name') or user.first_name
        last_name = data.get('last_name') or user.last_name
        
        if first_name:
            # Construct a cleaner username: "firstname.lastname"
            # LinkedIn OIDC guarantees first/last name are usually present
            name_parts = [first_name]
            if last_name:
                name_parts.append(last_name)
            
            base_username = ".".join(name_parts)
            # Slugify to ensure valid characters (e.g., Keshav Sahu -> keshav.sahu)
            clean_username = slugify(base_username)
            
            if clean_username:
                # generate_unique_username handles collision by appending numbers
                user.username = generate_unique_username([clean_username], 'user')
                
        return user

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        print("\n\n" + "="*50)
        print(f"SOCIAL AUTH ERROR: {provider_id}")
        if error:
            print(f"Error: {error}")
        if exception:
            print(f"Exception: {exception}")
            traceback.print_exc()
        if extra_context:
            print(f"Context: {extra_context}")
        print("="*50 + "\n\n")
        
        # Try to call super, but don't crash if it doesn't exist or signature is different
        try:
             super().authentication_error(request, provider_id, error=error, exception=exception, extra_context=extra_context)
        except Exception as e:
            print(f"Could not call super().authentication_error: {e}")
