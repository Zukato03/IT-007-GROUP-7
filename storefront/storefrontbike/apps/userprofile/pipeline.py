from django.shortcuts import redirect
from django.urls import reverse

def get_profile_data(strategy, details, user=None, *args, **kwargs):
    if user and not user.username:
        strategy.session_set('signup_google', True)
        return None  



