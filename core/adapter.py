from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import logging
import traceback

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
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
