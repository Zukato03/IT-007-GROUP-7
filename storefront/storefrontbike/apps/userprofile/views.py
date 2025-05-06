from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from django.core.mail import send_mail
from django.contrib.auth.models import User
from googleapiclient.discovery import build
from google.oauth2 import service_account

import json
import base64
from .forms import SignUpForm, UserprofileForm, ProfileCompletionForm
# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        userprofileForm = UserprofileForm(request.POST)

        if form.is_valid() and userprofileForm.is_valid():
            print("Form is valid")  
            user = form.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'

            print("Other profiles are valid.")
            userprofile = userprofileForm.save(commit=False)
            userprofile.user = user
            userprofile.save()

            login(request, user) 
            return redirect('frontpage')
        else:
            print("Form errors:", form.errors)
            print("UserProfile form errors:", userprofileForm.errors)

    else:
        form = SignUpForm()
        userprofileForm = UserprofileForm()

    return render(request, 'signup.html', {'form': form, 'userprofileForm': userprofileForm})

@login_required
def signup_google(request):
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            user.save()

            userprofile = form.save(commit=False)
            userprofile.user = user
            userprofile.save()
            
            return redirect('cart')
    else:
        form = ProfileCompletionForm(instance=request.user.userprofile)

    return render(request, 'signup_google.html', {'form': form})


@login_required
def myaccount(request):
    print("Request Method:", request.method)
    print("Request Headers:", request.headers)

    if request.session.get('signup_google'):
        del request.session['signup_google']
        return redirect('signup_google')  

    
    user = request.user
    user_profile = user.userprofile
    data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile': {
                'contact_number': user_profile.contact_number,
                'address': user_profile.address,
                'zip_code': user_profile.zip_code,
        }
    }

    # return JsonResponse(data)
    
    print("Google API Key:", settings.GOOGLE_API_KEY)
    print("User is logged in:", request.user.is_authenticated)
    return render(request, 'myaccount.html', {'google_api_key': settings.GOOGLE_API_KEY})
   


@login_required
@csrf_exempt 
def update_user_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.username = data['username']

        user_profile = user.userprofile
        
        user_profile.contact_number = data['contact_number']
        user_profile.address = data['address']
        user_profile.zip_code = data['zip_code']

        user.save()
        user_profile.save()
        print("Updated successfully")
        
        if data.get('password1') and data.get('password2') and data['password1'] == data['password2']:
            user.set_password(data['password1'])
            user.save()
            user_profile.save()
            update_session_auth_hash(request, user)
            print("Updated successfully")

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)



def forgot_username(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            send_forgot_username_email(user.username, email)
            return render(request, 'forgot_username_success.html')
        except User.DoesNotExist:
            return render(request, 'forgot_username.html', {'error': 'Email not associated with any account'})

    return render(request, 'forgotcredentials.html')

def send_forgot_username_email(username, email):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = service_account.Credentials.from_service_account_file('storefrontbike/token.json', scopes=SCOPES)

    service = build('gmail', 'v1', credentials=creds)
    message = {
        'raw': base64.urlsafe_b64encode(f"Subject: Forgot Username\n\nYour username is: {username}".encode()).decode()
    }
    
    service.users().messages().send(userId="me", body=message).execute()




