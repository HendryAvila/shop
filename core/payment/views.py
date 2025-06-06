from decimal import Decimal
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
import stripe
from django.conf import settings
from orders.models import Order
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

#creating the stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_process(request):
    logger.info("Starting payment process")
    order_id = request.session.get('order_id', None)
    logger.debug(f"Order ID from session: {order_id}")
    
    if not order_id:
        logger.warning("No order_id found in session")
        return redirect('cart:cart_detail')
    
    try:
        order = get_object_or_404(Order, id=order_id)
        logger.info(f"Order {order.id} retrieved successfully for payment")
        logger.debug(f"Order details - Email: {order.email}, Total: ${order.get_total_cost()}")
    except Exception as e:
        logger.error(f"Error retrieving order {order_id}: {str(e)}")
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        logger.debug("Processing POST request for payment")
        
        try:
            success_url = request.build_absolute_uri(reverse('payment:completed'))
            cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
            logger.debug(f"Payment URLs configured - Success: {success_url}, Cancel: {cancel_url}")
            
            #stripe session data
            session_data = {
                'mode': 'payment',
                'client_reference_id': order.id,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'line_items': []
            }
            
            logger.debug("Creating line items for Stripe session")
            for item in order.items.all():
                unit_amount = int(item.price * Decimal('100'))
                session_data['line_items'].append({
                    'price_data': {
                        'unit_amount': unit_amount,
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        },
                    },
                    'quantity': item.quantity,
                })
                logger.debug(f"Added line item: {item.product.name} x{item.quantity} - ${item.price}")
            
            logger.info("Creating Stripe checkout session")
            session = stripe.checkout.Session.create(**session_data)
            logger.info(f"Stripe session created successfully - ID: {session.id}")
            logger.debug(f"Redirecting to Stripe URL: {session.url}")
            
            return redirect(session.url, code=303)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error during payment process: {str(e)}")
            return render(request, 'payment/process.html', {
                'order': order,
                'error': 'Error processing payment. Please try again.'
            })
        except Exception as e:
            logger.error(f"Unexpected error during payment process: {str(e)}")
            return render(request, 'payment/process.html', {
                'order': order,
                'error': 'Technical error. Please contact support.'
            })
    else:
        logger.debug(f"Displaying payment form for order {order.id}")
        return render(request, 'payment/process.html', {'order': order})
    
def payment_completed(request):
    logger.info("Payment completed successfully")
    
    session_id = request.GET.get('session_id')
    if session_id:
        logger.debug(f"Payment completed with Stripe session ID: {session_id}")
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            logger.info(f"Stripe session verified - Status: {session.payment_status}")
            
            if session.client_reference_id:
                try:
                    order = Order.objects.get(id=session.client_reference_id)
                    logger.info(f"Payment completed for order {order.id} - Customer: {order.email}")
                    logger.debug(f"Payment amount: ${session.amount_total / 100} {session.currency.upper()}")
                except Order.DoesNotExist:
                    logger.warning(f"Order not found for completed payment: {session.client_reference_id}")
                    
        except stripe.error.StripeError as e:
            logger.error(f"Error verifying Stripe session: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error verifying payment: {str(e)}")
    else:
        logger.warning("Payment completed page accessed without session_id")
    
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    logger.warning("Payment was canceled")
    
    session_id = request.GET.get('session_id')
    if session_id:
        logger.debug(f"Payment canceled - Stripe session ID: {session_id}")
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            logger.debug(f"Canceled session status: {session.payment_status}")
            
            if session.client_reference_id:
                logger.warning(f"Payment canceled for order: {session.client_reference_id}")
                
        except Exception as e:
            logger.error(f"Error retrieving canceled session info: {str(e)}")
    else:
        logger.warning("Payment canceled page accessed without session_id")
    
    return render(request, 'payment/canceled.html')
