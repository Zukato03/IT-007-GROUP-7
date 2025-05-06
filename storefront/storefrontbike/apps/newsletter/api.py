import json

from django.http import JsonResponse

from .models import Subscriber

def api_add_subscriber(request): # Saving the email data from the newsletter email field.
    data = json.loads(request.body)
    email = data['email']

    subs = Subscriber.objects.create(email=email)

    return JsonResponse({'success': True})