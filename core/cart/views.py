import logging.config
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@require_POST
def cart_add(request, product_id):
    logger.info(f"Adding product to cart. Product ID: {product_id}")
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        logger.debug(f"Found product: {product.name}")
        
        form = CartAddProductForm(request.POST)
        logger.debug("Validating cart add form")
        
        if form.is_valid():
            cd = form.cleaned_data
            logger.debug(f"Form data: quantity={cd.get('quantity')}, override={cd.get('override')}")
            
            cart.add(product=product,
                    quantity=cd['quantity'],
                    overrite_quantity=cd['override'])
            logger.info(f"Successfully added {cd['quantity']} units of {product.name} to cart")
            return redirect('cart:cart_detail')
        else:
            logger.warning(f"Invalid form submission: {form.errors}")
            return redirect('shop:product_list')
    except Product.DoesNotExist:
        logger.error(f"Product not found with ID: {product_id}")
        return redirect('shop:product_list')
    except Exception as e:
        logger.error(f"Error adding product to cart: {str(e)}")
        return redirect('shop:product_list')

def cart_remove(request, product_id):
    logger.info(f"Removing product from cart. Product ID: {product_id}")
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        logger.debug(f"Found product: {product.name}")
        
        cart.remove(product)
        logger.info(f"Successfully removed {product.name} from cart")
        return redirect('cart:cart_detail')
    except Exception as e:
        logger.error(f"Error removing product from cart: {str(e)}")
        return redirect('cart:cart_detail')

def cart_detail(request):
    logger.info("Accessing cart detail view")
    try:
        cart = Cart(request)
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(
                initial={'quantity': item['quantity'],
                        'override': True})
        logger.debug(f"Cart contains {len(cart)} items")
        return render(request, 'cart/detail.html', {'cart': cart})
    except Exception as e:
        logger.error(f"Error displaying cart detail: {str(e)}")
        return redirect('shop:product_list')
