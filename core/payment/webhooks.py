import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
import logging
import os

logger = logging.getLogger(__name__)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    
    logger.info("WEBHOOK: Received!")
    
    # Debug info
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    logger.info(f"WEBHOOK: Secret configured: {bool(webhook_secret)}")
    if webhook_secret:
        logger.info(f"WEBHOOK: Secret starts with: {webhook_secret[:10]}...")
    logger.info(f"WEBHOOK: Signature header present: {bool(sig_header)}")
    logger.info(f"WEBHOOK: Payload size: {len(payload)} bytes")

    try:
        event = stripe.Webhook.construct_event(
                    payload,
                    sig_header,
                    settings.STRIPE_WEBHOOK_SECRET)
        logger.info(f"WEBHOOK: Event verified: {event.type}")
    except ValueError as e:
        logger.error(f"WEBHOOK: Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"WEBHOOK: Invalid signature: {e}")
        logger.error(f"WEBHOOK: Expected secret starts with: {webhook_secret[:10] if webhook_secret else 'None'}...")
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        logger.info(f"WEBHOOK: Processing checkout completion: {session.id}")
        
        if session.mode == 'payment' and session.payment_status == 'paid':
            order_id = session.client_reference_id
            logger.info(f"WEBHOOK: Looking for order ID: {order_id}")
            
            try:
                order = Order.objects.get(id=order_id)
                logger.info(f"WEBHOOK: Found order: {order.id} - {order.email}")
                
                # mark order as paid
                order.paid = True
                order.stripe_id = session.payment_intent
                # store Stripe payment ID (solo si el campo existe)
                if hasattr(order, 'stripe_id'):
                    order.stripe_id = session.payment_intent
                order.save()
                
                logger.info(f"WEBHOOK: Order {order.id} marked as PAID!")
                
            except Order.DoesNotExist:
                logger.error(f"WEBHOOK: Order not found: {order_id}")
                return HttpResponse(status=404)
        else:
            logger.warning(f"WEBHOOK: Payment not completed: mode={session.mode}, status={session.payment_status}")
    else:
        logger.info(f"WEBHOOK: Unhandled event type: {event.type}")

    return HttpResponse(status=200)