# 🚀 Guía Completa: Integración Stripe + Django

## 📋 Tabla de Contenidos
1. [Resumen General](#resumen-general)
2. [Flujo de Trabajo](#flujo-de-trabajo)
3. [Configuración Inicial](#configuración-inicial)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Implementación Paso a Paso](#implementación-paso-a-paso)
6. [Webhooks](#webhooks)
7. [Testing y Debugging](#testing-y-debugging)
8. [Troubleshooting](#troubleshooting)
9. [Checklist Final](#checklist-final)

---

## 🎯 Resumen General

Esta guía te ayudará a integrar Stripe en cualquier proyecto Django para procesar pagos de manera segura y eficiente.

### ¿Qué conseguirás?
- ✅ Procesar pagos con tarjeta de crédito
- ✅ Webhooks automáticos para confirmar pagos
- ✅ Interfaz segura con Stripe Checkout
- ✅ Gestión automática de órdenes
- ✅ Logs completos para debugging

---

## 🔄 Flujo de Trabajo

### Proceso Completo:
```
Usuario → Carrito → Orden → Stripe Checkout → Pago → Webhook → Confirmación
```

### Diagrama Visual:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Usuario   │───▶│   Carrito    │───▶│   Orden     │
│ Navega Shop │    │ Agrega Items │    │  Se Crea    │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Webhook    │◄───│    Stripe    │◄───│  Checkout   │
│ Confirma    │    │   Procesa    │    │   Pago      │
│  Orden      │    │    Pago      │    │  Seguro     │
└─────────────┘    └──────────────┘    └─────────────┘
      │
      ▼
┌─────────────┐
│   Admin     │
│ Orden Paid  │
│     ✅      │
└─────────────┘
```

---

## ⚙️ Configuración Inicial

### 1. Instalación de Dependencias

```bash
pip install stripe python-dotenv
```

### 2. Variables de Entorno

Crea archivo `.env` en la raíz del proyecto:

```env
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_tu_clave_publishable
STRIPE_SECRET_KEY=sk_test_tu_clave_secreta
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**⚠️ IMPORTANTE:** 
- NO uses espacios alrededor del `=`
- NO uses comillas
- El webhook secret debe estar completo

### 3. Configuración Django

```python
# settings.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
```

---

## 📁 Estructura del Proyecto

```
mi_proyecto/
├── .env                    # Variables de entorno
├── manage.py
├── mi_proyecto/
│   ├── settings.py
│   └── urls.py
├── orders/                 # App de órdenes
│   ├── models.py          # Modelo Order
│   ├── views.py           # Crear órdenes
│   ├── forms.py           # Formularios
│   └── admin.py           # Admin interface
├── payment/               # App de pagos
│   ├── views.py           # Lógica de pago
│   ├── webhooks.py        # Webhooks de Stripe
│   ├── urls.py            # URLs de pago
│   └── templates/payment/ # Templates
└── shop/                  # App principal
    ├── models.py          # Productos
    └── views.py           # Catálogo
```

---

## 🛠️ Implementación Paso a Paso

### Paso 1: Crear App Payment

```bash
python manage.py startapp payment
```

### Paso 2: Configurar INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ... apps existentes
    'payment.apps.PaymentConfig',
]
```

### Paso 3: Modelo Order

```python
# orders/models.py
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

### Paso 4: Admin Interface

```python
# orders/admin.py
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

### Paso 5: Views de Payment

```python
# payment/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import stripe
from django.conf import settings
from orders.models import Order

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_process(request):
    order_id = request.session.get('order_id', None)
    
    if not order_id:
        return redirect('cart:cart_detail')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
        
        # Datos de la sesión de Stripe
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,  # ¡CRÍTICO!
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        
        # Agregar items de la orden
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
        
        # Crear sesión de Stripe
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    
    return render(request, 'payment/process.html', {'order': order})

def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
```

### Paso 6: Webhooks (¡CRÍTICO!)

```python
# payment/webhooks.py
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
                order.stripe_id = session.payment_intent
                order.save()
                
                logger.info(f"WEBHOOK: Order {order.id} marked as PAID!")
                
            except Order.DoesNotExist:
                logger.error(f"WEBHOOK: Order {order_id} not found")
                return HttpResponse(status=404)

    return HttpResponse(status=200)
```

### Paso 7: URLs

```python
# payment/urls.py
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

```python
# urls.py principal
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payment/', include('payment.urls', namespace='payment')),
    # ... otras URLs
]
```

---

## 🔗 Webhooks

### ¿Qué son?
Los webhooks son notificaciones automáticas que Stripe envía cuando ocurre un evento.

### Flujo:
```
Pago Exitoso → Stripe → Webhook → Tu Servidor → Marca Orden como Pagada
```

### Configuración Desarrollo:

1. **Instalar Stripe CLI:**
   ```bash
   # Windows (con Scoop)
   scoop install stripe
   
   # Mac
   brew install stripe/stripe-cli/stripe
   ```

2. **Autenticar:**
   ```bash
   stripe login
   ```

3. **Escuchar webhooks:**
   ```bash
   stripe listen --forward-to localhost:8000/payment/webhook/
   ```

4. **Copiar webhook secret** al `.env`

### Configuración Producción:

1. Dashboard Stripe → Developers → Webhooks
2. Add endpoint: `https://tudominio.com/payment/webhook/`
3. Eventos: `checkout.session.completed`
4. Copiar webhook secret

---

## 🧪 Testing y Debugging

### Script de Verificación:

```python
# check_stripe.py
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
```

### Tarjetas de Prueba:

| Tipo | Número | Resultado |
|------|--------|-----------|
| Exitosa | 4242 4242 4242 4242 | Pago aprobado |
| Rechazada | 4000 0000 0000 0002 | Pago rechazado |
| 3D Secure | 4000 0000 0000 3220 | Requiere autenticación |

### Configurar Logging:

```python
# settings.py
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

---

## 🚨 Troubleshooting

### Errores Comunes:

#### 1. "Invalid signature"
**Causa:** Webhook secret incorrecto  
**Solución:** 
- Verificar formato en `.env` (sin espacios, sin comillas)
- Copiar secret completo de Stripe CLI
- Reiniciar servidor Django

#### 2. "Order not found"
**Causa:** `client_reference_id` no se envía  
**Solución:** 
- Verificar `'client_reference_id': order.id` en session_data

#### 3. "UnicodeEncodeError" (Windows)
**Causa:** Emojis en logs  
**Solución:** 
- Usar solo texto ASCII en logs

#### 4. Error 404 en webhook
**Causa:** URL incorrecta  
**Solución:** 
- URL debe ser `/payment/webhook/` (con barra final)

### Debugging Checklist:

- [ ] Variables de entorno correctas
- [ ] Stripe CLI ejecutándose
- [ ] Servidor Django activo
- [ ] URLs configuradas
- [ ] Webhooks llegando a logs
- [ ] `client_reference_id` en sesión
- [ ] Campo `paid` en modelo Order

---

## ✅ Checklist Final

### Desarrollo:
- [ ] Instalar `stripe` y `python-dotenv`
- [ ] Configurar `.env`
- [ ] Crear app `payment`
- [ ] Modelos `Order` y `OrderItem`
- [ ] Views de payment
- [ ] Webhook handler
- [ ] URLs configuradas
- [ ] Stripe CLI funcionando
- [ ] Probar flujo completo

### Producción:
- [ ] Webhook endpoint en Dashboard
- [ ] Claves de producción
- [ ] HTTPS configurado
- [ ] Pruebas con tarjetas reales
- [ ] Monitoreo de logs
- [ ] Alertas de error

---

## 🎯 Puntos Clave

### Los 5 Elementos Críticos:

1. **`client_reference_id`** - Conecta sesión con orden
2. **Webhook secret** - Debe ser exacto
3. **Logs detallados** - Para debugging
4. **Stripe CLI** - Para desarrollo
5. **Reiniciar servidor** - Tras cambios en `.env`

### Flujo de Debugging:

```
¿Llegan los webhooks? → ¿Se verifican? → ¿Se encuentra la orden? → ¿Se marca como pagada?
```

---

## 📚 Recursos

- [Documentación Stripe](https://stripe.com/docs)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [Testing Cards](https://stripe.com/docs/testing)
- [Webhooks Guide](https://stripe.com/docs/webhooks)

---

## 🚀 Template Rápido

Para nuevos proyectos, copia estos archivos básicos:

1. **`.env`** - Variables de configuración
2. **`payment/views.py`** - Lógica de pago
3. **`payment/webhooks.py`** - Handler de webhooks
4. **`payment/urls.py`** - URLs de payment
5. **`check_stripe.py`** - Script de verificación

**¡Con esta guía tendrás Stripe funcionando en cualquier proyecto Django! 🎉** 