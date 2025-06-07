from django.db import models
from shop.models import Product
from django.conf import settings
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['-created']
        indexes = [
                models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        logger.debug(f"Calculating total cost for order {self.id}")
        try:
            total = sum(item.get_cost() for item in self.items.all())
            logger.info(f"Total cost for order {self.id}: {total}")
            return total
        except Exception as e:
            logger.error(f"Error calculating total cost for order {self.id}: {str(e)}")
            raise

    def save(self, *args, **kwargs):
        logger.info(f"Saving order for {self.first_name} {self.last_name}")
        try:
            super().save(*args, **kwargs)
            logger.debug(f"Order {self.id} saved successfully")
        except Exception as e:
            logger.error(f"Error saving order: {str(e)}")
            raise
        
    def get_stripe_url(self):
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)

    def get_cost(self):
        logger.debug(f"Calculating cost for order item {self.id}")
        try:
            cost = self.price * self.quantity
            logger.debug(f"Cost for order item {self.id}: {cost}")
            return cost
        except Exception as e:
            logger.error(f"Error calculating cost for order item {self.id}: {str(e)}")
            raise

    def save(self, *args, **kwargs):
        logger.info(f"Saving order item for product {self.product.name} in order {self.order.id}")
        try:
            super().save(*args, **kwargs)
            logger.debug(f"Order item {self.id} saved successfully")
        except Exception as e:
            logger.error(f"Error saving order item: {str(e)}")
            raise

