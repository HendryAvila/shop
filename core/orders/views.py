from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import create_order
import logging
from django.contrib.staticfiles import finders
import os

# Configure logger for this module
logger = logging.getLogger(__name__)

def order_create(request):
    logger.info("Starting order creation process")
    cart = Cart(request)
    
    if request.method == "POST":
        logger.debug("Processing POST request for order creation")
        form = OrderCreateForm(request.POST)
        
        if form.is_valid():
            logger.debug("Order form is valid, creating order")
            try:
                order = form.save()
                logger.info(f"Order {order.id} created successfully")
                
                for item in cart:
                    logger.debug(f"Creating order item for product: {item['product'].name}")
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                
                cart.clear()
                create_order.delay(order.id)
                logger.info("setting the order in the session")
                request.session['order_id'] = order.id
                logger.info("Cart cleared after successful order creation")
                return redirect(reverse('payment:process'))
            
            except Exception as e:
                logger.error(f"Error during order creation: {str(e)}")
                raise
        else:
            logger.warning(f"Invalid form submission: {form.errors}")
    else:
        logger.debug("Displaying empty order form")
        form = OrderCreateForm()
    
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    template_path = 'orders/order/pdf.html'
    context = {'order': order}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

    template = get_template(template_path)
    html = template.render(context)
    
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources.
    """
    # use short variable names
    static_url = settings.STATIC_URL  # Typically /static/
    static_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    media_url = settings.MEDIA_URL  # Typically /media/
    media_root = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    if uri.startswith(media_url):
        path = os.path.join(media_root, uri.replace(media_url, ""))
    elif uri.startswith(static_url):
        # First, search in STATIC_ROOT
        path = os.path.join(static_root, uri.replace(static_url, ""))
        if not os.path.exists(path):
            # If not found, search with finders
            path = finders.find(uri.replace(static_url, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    if not path:
        raise Exception(
            'media URI must start with %s or %s' % (static_url, media_url)
        )
    return path