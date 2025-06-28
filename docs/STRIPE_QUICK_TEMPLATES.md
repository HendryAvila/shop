# 🚀 Templates Rápidos para Stripe + Django

## 📁 Archivos Esenciales

### 1. `.env` Template

```env
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_REEMPLAZAR_CON_TU_CLAVE
STRIPE_SECRET_KEY=sk_test_REEMPLAZAR_CON_TU_CLAVE
STRIPE_WEBHOOK_SECRET=whsec_COPIAR_DE_STRIPE_CLI

# Email Configuration (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### 2. `payment/views.py` Template

```python
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import stripe
from django.conf import settings
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_process(request):
    order_id = request.session.get('order_id', None)
    
    if not order_id:
        return redirect('cart:cart_detail')  # Cambiar según tu app
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
        
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,  # ¡CRÍTICO!
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })
        
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    
    return render(request, 'payment/process.html', {'order': order})

def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
```

### 3. `payment/webhooks.py` Template

```python
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    
    logger.info("WEBHOOK: Received!")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"WEBHOOK: Event verified: {event.type}")
    except ValueError as e:
        logger.error(f"WEBHOOK: Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"WEBHOOK: Invalid signature: {e}")
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        
        if session.mode == 'payment' and session.payment_status == 'paid':
            order_id = session.client_reference_id
            logger.info(f"WEBHOOK: Processing payment for order {order_id}")
            
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.stripe_id = session.payment_intent  # Opcional
                order.save()
                
                logger.info(f"WEBHOOK: Order {order.id} marked as PAID!")
                
            except Order.DoesNotExist:
                logger.error(f"WEBHOOK: Order {order_id} not found")
                return HttpResponse(status=404)

    return HttpResponse(status=200)
```

### 4. `payment/urls.py` Template

```python
from django.urls import path
from . import views, webhooks

app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]
```

### 5. `settings.py` Additions

```python
# Agregar al final de settings.py

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Logging para Payment
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'payment': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
```

### 6. `orders/models.py` Template

```python
from django.db import models

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
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('shop.Product', related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.price * self.quantity
```

### 7. `orders/admin.py` Template

```python
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'paid', 'created']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
```

### 8. `check_stripe.py` Script

```python
import os
from dotenv import load_dotenv

load_dotenv()

print("=== VERIFICACIÓN STRIPE ===")
print(f"STRIPE_SECRET_KEY: {'✅' if os.getenv('STRIPE_SECRET_KEY') else '❌'}")
print(f"STRIPE_PUBLISHABLE_KEY: {'✅' if os.getenv('STRIPE_PUBLISHABLE_KEY') else '❌'}")

webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
if webhook_secret:
    print(f"STRIPE_WEBHOOK_SECRET: ✅ ({webhook_secret[:10]}...)")
else:
    print("STRIPE_WEBHOOK_SECRET: ❌ FALTANTE")
    print("Ejecuta: stripe listen --forward-to localhost:8000/payment/webhook/")
```

---

## 🚀 Setup Rápido (5 minutos)

### Paso 1: Instalar
```bash
pip install stripe python-dotenv
```

### Paso 2: Crear .env
```bash
# Copia el template de arriba
```

### Paso 3: Apps en settings.py
```python
INSTALLED_APPS = [
    # ... existentes
    'payment.apps.PaymentConfig',
]
```

### Paso 4: Crear payment app
```bash
python manage.py startapp payment
```

### Paso 5: Copiar archivos
- `payment/views.py`
- `payment/webhooks.py` 
- `payment/urls.py`

### Paso 6: URLs principales
```python
# urls.py
urlpatterns = [
    path('payment/', include('payment.urls', namespace='payment')),
]
```

### Paso 7: Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 8: Stripe CLI
```bash
stripe listen --forward-to localhost:8000/payment/webhook/
# Copiar webhook secret al .env
```

### Paso 9: Test
```bash
python check_stripe.py
python manage.py runserver
```

---

## 🎯 Checklist Express

- [ ] ✅ `pip install stripe python-dotenv`
- [ ] ✅ Crear `.env` con claves
- [ ] ✅ Agregar payment a INSTALLED_APPS
- [ ] ✅ Copiar templates de archivos
- [ ] ✅ Configurar URLs
- [ ] ✅ Ejecutar migraciones
- [ ] ✅ Iniciar Stripe CLI
- [ ] ✅ Copiar webhook secret
- [ ] ✅ Probar con script check_stripe.py

**¡En 5 minutos tienes Stripe funcionando! 🎉** 