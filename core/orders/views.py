from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import create_order
import logging

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
