import json
import stripe
import requests
import hmac
import hashlib

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from django.db import transaction

from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64

from apps.cart.models import Cart
from apps.order.models import Order, PaymentTracking 
from apps.store.models import Product
from apps.order.views import render_to_pdf
from apps.store.api import create_checkout_session
from apps.order.utils import checkout
from datetime import datetime
from storefrontbike.gmail_utils import send_gmail_email


@csrf_exempt
def webhook(request):
    payload = request.body
    event = None

    stripe.api_key = settings.STRIPE_API_KEYS_HIDDEN

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session_id = event['data']['object']['id']
        print(f"Session id: {session_id}")

        try:
            tracking = PaymentTracking.objects.get(session_id=session_id)
            order_id = tracking.order_id

            with transaction.atomic():  # Ensure all actions happen together
                order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
                order.ordered_date = datetime.now()
                order.paid = True
                order.payment_intent = event['data']['object']['payment_intent']
                order.save()

                # Update product stock
                for item in order.items.all():
                    product = item.product
                    product.number_available -= item.quantity
                    product.save()

                # Clear the cart for the user
                cart = Cart.objects.filter(user=order.user).first()  # Adjust this query if needed
                if cart:
                    cart.items.filter(product__in=[item.product for item in order.items.all()]).delete()
                    print(f"Cart cleared for user {order.user.username}.")

                print("Order updated successfully with Payment Intent: ", order.payment_intent)

                send_order_confirmation_email(order)

        except PaymentTracking.DoesNotExist:
            print(f"No tracking found for session ID: {session_id}. Deleting the order...")
            delete_order_by_session(session_id)
            return HttpResponse(status=404)

        except Order.DoesNotExist:
            print(f"Order not found for order ID: {order_id}. Deleting the order...")
            delete_order_by_session(session_id)
            return HttpResponse(status=404)

    return HttpResponse(status=200)

"""
            subject = 'Order confirmation'
            from_email = 'noreply@siklomnl.com'
            to = ['mail@siklomnl.com', order.email]
            text_content = 'Your order is successful'
            html_content = render_to_string('order_confirmation.html', {'order': order})

            pdf = render_to_pdf('order_pdf.html', {'order': order})

            message_to_email = EmailMultiAlternatives(subject, text_content, from_email, to)
            message_to_email.attach_alternative(html_content, "text/html")

            if pdf:
                name = 'order_%s.pdf' % order.id
                message_to_email.attach(name, pdf, 'application/pdf')

            message_to_email.send()
            #html = render_to_string('order_confirmation.html', {'order': order})
            #send_mail('Order confirmation', 'Your order has been sent!', 'noreply@siklomnl.com', ['mail@siklomnl.com', order.email], fail_silently=False, html_message=html)
            #print('Email sent.')

            """

def delete_order_by_session(session_id):
    try:
        tracking = PaymentTracking.objects.get(session_id=session_id)
        order = Order.objects.get(id=tracking.order_id)
        
        order.delete()
        tracking.delete()
        print(f"Order {order.id} and PaymentTracking {session_id} deleted successfully.")
        
    except PaymentTracking.DoesNotExist:
        print(f"No PaymentTracking found for session ID {session_id}.")
    except Order.DoesNotExist:
        print(f"No Order found for PaymentTracking session ID {session_id}.")

# """
# @csrf_exempt
# def paymongo_webhook(request):
#     payload = request.body
#     paymongo_sig = request.headers.get('Paymongo-Signature')

#     if not paymongo_sig:
#         return HttpResponse(status=400)
    
#     secret = settings.PAYMONGO_WEBHOOK_SECRET
#     digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

#     if not hmac.compare_digest(digest, paymongo_sig):
#         return HttpResponse(status=400)

#     event = json.loads(payload)

#     try:
#         if event['data']['attributes']['status'] == 'succeeded':
#             session_id = event['data']['id']  
#             payment_intent = event['data']['attributes']['payment_intent_id']

#             try:
#                 tracking = PaymentTracking.objects.get(session_id=session_id)
#                 order = Order.objects.get(id=tracking.order_id)

#                 order.paid = True
#                 order.payment_intent = payment_intent
#                 order.save()

#                 for item in order.items.all():
#                     product = item.product
#                     product.number_available -= item.quantity
#                     product.save()

#                 # Send order confirmation email
#                 send_order_confirmation_email(order)

#                 print(f"Order {order.id} updated successfully with Payment Intent: {payment_intent}")
#                 return HttpResponse(status=200)

#             except PaymentTracking.DoesNotExist:
#                 print("No tracking found for session ID.")
#                 return HttpResponse(status=404)
#             except Order.DoesNotExist:
#                 print(f"Order not found for order ID: {tracking.order_id}")
#                 return HttpResponse(status=404)
#     except KeyError as e:
#         print(f"Error processing webhook: {str(e)}")
#         return HttpResponse(status=400)

#     return HttpResponse(status=200)
# """


"""
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SERVICE_ACCOUNT_FILE = 'path/to/credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
"""


def send_order_confirmation_email(order):
    subject = 'Order Confirmation'
    to_email = order.email
    
    message_text = f"Good day, dear Customer."
    
    # Render the HTML content for the email body
    html_content = render_to_string('order_confirmation_email.html', {'order': order})

    # Render PDF if required
    pdf_content = render_to_pdf('order_pdf.html', {'order': order})
    pdf_filename = f'order_{order.id}.pdf' if pdf_content else None

    # Send the email with HTML content, PDF, and other details
    send_gmail_email(
        to_email=to_email,
        subject=subject,
        message_text=message_text,
        html_content=html_content,
        pdf_content=pdf_content,
        pdf_filename=pdf_filename
    )
