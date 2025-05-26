from django.db import models
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        logger.debug(f"Generating URL for category: {self.name}")
        url = reverse('shop:product_list_by_category', args=[self.slug])
        logger.debug(f"Generated URL: {url}")
        return url
    
    def save(self, *args, **kwargs):
        logger.info(f"Saving category: {self.name}")
        try:
            super().save(*args, **kwargs)
            logger.debug(f"Category {self.name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving category {self.name}: {str(e)}")
            raise
    
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        logger.debug(f"Generating URL for product: {self.name}")
        url = reverse('shop:product_detail', args=[self.id, self.slug])
        logger.debug(f"Generated URL: {url}")
        return url

    def save(self, *args, **kwargs):
        logger.info(f"Saving product: {self.name} in category: {self.category.name}")
        try:
            super().save(*args, **kwargs)
            logger.debug(f"Product {self.name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving product {self.name}: {str(e)}")
            raise

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting product: {self.name} from category: {self.category.name}")
        try:
            super().delete(*args, **kwargs)
            logger.info(f"Product {self.name} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting product {self.name}: {str(e)}")
            raise
