from decimal import Decimal
from django.conf import settings
from shop.models import Product
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

class Cart():
    """
    A base cart class, providing some default behaviors that can be inherited or overrided, as necessary.
    take the request's sesion
    with the request session get the cart id, the cart id is the session id
    if the cart id is not in the session, create a new cart id and store it in the session
    if the cart id is in the session, get the cart from the session
    """
    def __init__(self,request):
        logger.debug(f"Initializing cart for session: {request.session.session_key}")
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            logger.info("No cart found in session. Creating new cart")
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        logger.debug(f"Cart initialized with {len(cart)} items")
    
    def add(self, product, quantity=1, overrite_quantity=False):
        """_summary_

        Args:
            product (_type_): Models.Product
            quantity (int, optional): numbers of items. Defaults to 1.
            overrite_quantity (bool, optional): flag to check if the quantity should be overrited or add to the existing quantity. Defaults to False.
        """
        try:
            product_id = str(product.id)
            logger.debug(f"Adding product ID {product_id} to cart. Quantity: {quantity}, Override: {overrite_quantity}")
            
            if product_id not in self.cart:
                logger.info(f"New product added to cart: {product.name} (ID: {product_id})")
                self.cart[product_id] = {'quantity':0, 'price': str(product.price)}
            
            if overrite_quantity:
                logger.debug(f"Overwriting quantity to {quantity} for product {product_id}")
                self.cart[product_id]['quantity'] = quantity
            else:
                new_quantity = self.cart[product_id]['quantity'] + quantity
                logger.debug(f"Updating quantity from {self.cart[product_id]['quantity']} to {new_quantity} for product {product_id}")
                self.cart[product_id]['quantity'] += quantity
            
            self.save()
            logger.info(f"Product {product_id} successfully added to cart")
        except Exception as e:
            logger.error(f"Error adding product {product_id} to cart: {str(e)}")
            raise

    def save(self):
        """
        mark the session as modified to make sure it gets saved
        """
        logger.debug("Marking session as modified")
        self.session.modified = True
        logger.debug("Session successfully marked as modified")

    def remove(self, product):
        """
        remove an item from the cart
        """
        try:
            product_id = str(product.id)
            logger.debug(f"Attempting to remove product {product_id} from cart")
            
            if product_id in self.cart:
                logger.info(f"Removing product {product_id} from cart")
                del self.cart[product_id]
                self.save()
                logger.debug(f"Product {product_id} successfully removed from cart")
            else:
                logger.warning(f"Attempted to remove non-existent product {product_id} from cart")
        except Exception as e:
            logger.error(f"Error removing product {product_id} from cart: {str(e)}")
            raise

    def __iter__(self):
        """
        collect the product_id in the session data to the product objects
        """
        logger.debug("Starting cart iteration")
        try:
            product_ids = self.cart.keys()
            logger.debug(f"Fetching products with IDs: {list(product_ids)}")
            
            products = Product.objects.filter(id__in=product_ids)
            logger.debug(f"Found {len(products)} products in database")
            
            for product in products:
                self.cart[str(product.id)]['product'] = product
                logger.debug(f"Added product details for ID {product.id}")

            for item in self.cart.values():
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                logger.debug(f"Calculated total price for item: {item['total_price']}")
                yield item
                
            logger.debug("Finished cart iteration")
        except Exception as e:
            logger.error(f"Error during cart iteration: {str(e)}")
            raise

    def __len__(self):
        """
        count all items in the cart
        """
        total_items = sum(item['quantity'] for item in self.cart.values())
        logger.debug(f"Cart contains {total_items} items in total")
        return total_items

    def get_total_price(self):
        """
        get the total price of the cart
        """
        try:
            total = sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
            logger.debug(f"Calculated total cart price: {total}")
            return total
        except Exception as e:
            logger.error(f"Error calculating total price: {str(e)}")
            raise

    def clear(self):
        """
        remove cart from session
        """
        try:
            logger.info("Clearing cart from session")
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True
            logger.debug("Cart successfully cleared from session")
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            raise