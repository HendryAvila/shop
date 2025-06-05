from celery import shared_task
from .models import Order
from django.core.mail import send_mail
import logging
from django.conf import settings
from decimal import Decimal

# Configurar el logger para las tareas de orders
logger = logging.getLogger('core.orders')

def format_price(price: Decimal) -> str:
    """Format price with 2 decimal places and currency symbol."""
    return f"${price:.2f}"

@shared_task
def create_order(order_id):
    """
    Task to send an email notification when an order is created.

    Args:
        order_id (int): The ID of the order that was created

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    logger.info(f"Starting email task for order ID: {order_id}")
    
    try:
        order = Order.objects.get(id=order_id)
        logger.debug(f"Order retrieved successfully: {order}")

        # Create a detailed order summary
        order_items = [
            f"• {item.quantity}x {item.product.name} - {format_price(item.get_cost())}"
            for item in order.items.all()
        ]
        
        items_summary = "\n".join(order_items)
        
        subject = f"Order Confirmation #{order.id} - Thank you for your purchase!"
        
        message = f"""Dear {order.first_name} {order.last_name},

Thank you for shopping with us! We're pleased to confirm that your order has been successfully received.

Order Details:
-------------
Order Number: #{order.id}
Date: {order.created.strftime('%B %d, %Y')}

Shipping Address:
----------------
{order.first_name} {order.last_name}
{order.address}
{order.postal_code} {order.city}

Order Summary:
-------------
{items_summary}

Subtotal: {format_price(order.get_total_cost())}
Shipping: {format_price(Decimal('0.00'))}  
Total: {format_price(order.get_total_cost())}

Payment Status: Completed
Shipping Method: Standard Delivery

What's Next?
-----------
1. You'll receive a shipping confirmation email once your order is dispatched
2. You can track your order status by logging into your account
3. If you have any questions, please contact our customer service

Thank you for choosing our shop! We appreciate your business.

Best regards,
The Shop Team

Note: This is an automated message, please do not reply to this email.
For support, please contact support@shop.com
"""
        
        logger.debug(f"Attempting to send email to: {order.email}")
        mail_sent = send_mail(
            subject,
            message,
            "bloghendrytest@gmail.com",
            [order.email],
            fail_silently=False,
        )

        if mail_sent:
            logger.info(f"Email sent successfully for order ID: {order_id}")
        else:
            logger.error(f"Failed to send email for order ID: {order_id}")

        return mail_sent

    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} not found")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while processing order {order_id}: {str(e)}")
        raise
