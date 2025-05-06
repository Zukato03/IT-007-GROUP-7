import datetime

from django.urls import reverse
from django.contrib import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from apps.order.views import render_to_pdf

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .models import Order, OrderItem, PaymentTracking

# Register your models here.
def send_gmail_api_email(subject, body, to, attachment=None):
    creds = Credentials.from_authorized_user_file('storefrontbike/token.json', ['https://www.googleapis.com/auth/gmail.send'])
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'html'))
    
    if attachment:
        part = MIMEBase('application', 'pdf')
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='order.pdf')
        message.attach(part)
    
    encoded_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    print(f"Sending email to {to}")
    try:
        send_message = service.users().messages().send(userId="me", body=encoded_message).execute()
        print(f"Message sent to {to}, ID: {send_message['id']}")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

def order_name(obj):
    return '%s %s' % (obj.first_name, obj.last_name)

order_name.short_description = 'Name'

def admin_order_shipped(ModelAdmin, request, queryset):
    for order in queryset:
        order.shipped_date = datetime.datetime.now()
        order.shipped_status = Order.SHIPPED
        order.save()

        html = render_to_string('order_shipped_email.html', {'order': order})
        
        pdf_attachment = render_to_pdf('order_pdf.html', {'order': order})
        
        send_gmail_api_email(
            'Order Shipped',
            html,
            order.email,
            attachment=pdf_attachment
        )
    return

admin_order_shipped.short_description = 'Set shipped'

def admin_order_delivered(ModelAdmin, request, queryset):
    for order in queryset:
        order.delivered_date = datetime.datetime.now()
        order.shipped_status = Order.DELIVERED
        order.save()

        html = render_to_string('order_delivered_email.html', {'order': order})
        
        pdf_attachment = render_to_pdf('order_pdf.html', {'order': order})
        

        send_gmail_api_email(
            'Order Delivered',
            html,
            order.email,
            attachment=pdf_attachment
        )
    return

admin_order_delivered.short_description = 'Set delivered'
# def send_gmail_api_email(subject, body, to):
#     creds = Credentials.from_authorized_user_file('storefrontbike/token.json', ['https://www.googleapis.com/auth/gmail.send'])
#     service = build('gmail', 'v1', credentials=creds)
    
#     message = MIMEMultipart()
#     message['to'] = to
#     message['subject'] = subject
#     message.attach(MIMEText(body, 'html'))
    
#     encoded_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
#     print(f"Sending email to {to}")
#     try:
#         send_message = service.users().messages().send(userId="me", body=encoded_message).execute()
#         print(f"Message sent to {to}, ID: {send_message['id']}")
#     except Exception as e:
#         print(f"An error occurred while sending email: {e}")

# def order_name(obj): # Combining first name and last name
#     return '%s %s' % (obj.first_name, obj.last_name)

# order_name.short_description = 'Name'

# def admin_order_shipped(ModelAdmin, request, queryset):
#     for order in queryset:
#         order.shipped_date = datetime.datetime.now()
#         order.shipped_status = Order.SHIPPED
#         order.save()

#         html = render_to_string('order_sent.html', {'order': order})
#         send_gmail_api_email(
#             'Order Shipped',
#             html,
#             order.email
#         )
#     return

# admin_order_shipped.short_description = 'Set shipped'

# def admin_order_delivered(ModelAdmin, request, queryset):
#     for order in queryset:
#         order.delivered_date = datetime.datetime.now()
#         order.shipped_status = Order.DELIVERED
#         order.save()

#         html = render_to_string('order_sent.html', {'order': order})
#         send_gmail_api_email(
#             'Order Delivered',
#             html,
#             order.email
#         )
#     return

# admin_order_delivered.short_description = 'Set delivered'

def order_pdf(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(reverse('admin_order_pdf', args=[obj.id])))

order_pdf.short_description = 'PDF Title'

def get_search_results(self, request, queryset, search_term):
    if search_term:
        try:
            year, month, day = map(int, search_term.split('-'))
            queryset = queryset.filter(
                order_created_at__year=year,
                order_created_at__month=month,
                order_created_at__day=day
            )
            return queryset, False 
        except ValueError:
            pass  
        
        try:
            year, month = map(int, search_term.split('-'))
            queryset = queryset.filter(
                order_created_at__year=year,
                order_created_at__month=month
            )
            return queryset, False  
        except ValueError:
            pass 

        try:
            year = int(search_term)
            queryset = queryset.filter(order_created_at__year=year)
            return queryset, False 
        except ValueError:
            pass  

    return super().get_search_results(request, queryset, search_term)


class OrderItemInLine(admin.TabularInline): # To show the ordered items.
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', order_name, 'shipped_status', 'order_created_at', order_pdf]
    list_filter = ['order_created_at', 'shipped_status']
    search_fields = ['first_name', 'last_name', 'address', 'contact_number', 'order_created_at']  # Existing fields
    
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            try:
                year, month, day = map(int, search_term.split('-'))
                queryset = queryset.filter(order_created_at__year=year, order_created_at__month=month, order_created_at__day=day)
                return queryset, False 
            except ValueError:
                pass  
        
        return super().get_search_results(request, queryset, search_term)

    def save_model(self, request, obj, form, change):
        if not change:  
            super().save_model(request, obj, form, change)
            return

        if obj.shipped_status == Order.SHIPPED:
            html = render_to_string('order_sent.html', {'order': obj})
            send_gmail_api_email(
                'Order Shipped',
                html,
                obj.email
            )
        elif obj.shipped_status == Order.DELIVERED:
            html = render_to_string('order_sent.html', {'order': obj})
            send_gmail_api_email(
                'Order Delivered',
                html,
                obj.email
            )

        super().save_model(request, obj, form, change)

    inlines = [OrderItemInLine]
    actions = [admin_order_shipped, admin_order_delivered]

admin.site.register(Order, OrderAdmin)
#admin.site.register(OrderItem)
#admin.site.register(PaymentTracking)
