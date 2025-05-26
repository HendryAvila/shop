from django.shortcuts import render, get_object_or_404
from .models import Category, Product
import logging

logger = logging.getLogger(__name__)

def product_list(request, category_slug=None):
    logger.info(f"Accessing product list view. Category slug: {category_slug}")
    try:
        category = None
        categories = Category.objects.all()
        logger.debug(f"Found {categories.count()} categories")
        
        products = Product.objects.filter(available=True)
        logger.debug(f"Found {products.count()} available products")
        
        if category_slug:
            logger.debug(f"Filtering by category slug: {category_slug}")
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
            logger.debug(f"Found {products.count()} products in category {category.name}")
        
        context = {
            'category': category,
            'products': products,
            'categories': categories
        }
        logger.debug("Rendering product list template")
        return render(request, 'shop/product/list.html', context)
    except Exception as e:
        logger.error(f"Error in product_list view: {str(e)}")
        raise
    
def product_detail(request, id, slug):
    logger.info(f"Accessing product detail view. Product ID: {id}, Slug: {slug}")
    try:
        product = get_object_or_404(Product,
                                  id=id,
                                  slug=slug,
                                  available=True)
        logger.debug(f"Found product: {product.name}")
        
        context = {'product': product}
        logger.debug("Rendering product detail template")
        return render(request, 'shop/product/detail.html', context)
    except Product.DoesNotExist:
        logger.warning(f"Product not found. ID: {id}, Slug: {slug}")
        raise
    except Exception as e:
        logger.error(f"Error in product_detail view: {str(e)}")
        raise