from io import BytesIO
from celery import shared_task
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
import os
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources.
    """
    # use short variable names
    static_url = settings.STATIC_URL
    static_root = settings.STATIC_ROOT
    media_url = settings.MEDIA_URL
    media_root = settings.MEDIA_ROOT

    if uri.startswith(media_url):
        path = os.path.join(media_root, uri.replace(media_url, ""))
    elif uri.startswith(static_url):
        # First, search in STATIC_ROOT
        path = os.path.join(static_root, uri.replace(static_url, ""))
        if not os.path.exists(path):
            # If not found, search with finders
            path = finders.find(uri.replace(static_url, ""))
    else:
        return uri

    if not path:
        raise Exception(
            'media URI must start with %s or %s' % (static_url, media_url)
        )
    return path

@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    logger.info(f"Starting payment_completed task for order ID: {order_id}")
    try:
        order = Order.objects.get(id=order_id)

        # create invoice e-mail
        subject = f'My Shop - Invoice no. {order.id}'
        message = 'Please, find attached the invoice for your recent purchase.'
        email = EmailMessage(subject,
                             message,
                             'admin@myshop.com',
                             [order.email])
        
        # generate PDF
        template_path = 'orders/order/pdf.html'
        context = {'order': order}
        template = get_template(template_path)
        html = template.render(context)
        
        result = BytesIO()
        pdf_status = pisa.CreatePDF(html, dest=result, link_callback=link_callback)
        
        if pdf_status.err:
            logger.error(f"Error generating PDF for order {order_id}: {pdf_status.err}")
            return False

        # attach PDF file
        email.attach(f'order_{order.id}.pdf',
                     result.getvalue(),
                     'application/pdf')
        # send e-mail
        email.send()
        logger.info(f"Email with invoice sent successfully for order ID: {order_id}")
        return True
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} not found in payment_completed task.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in payment_completed task for order {order_id}: {e}")
        return False 