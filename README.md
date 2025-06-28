# E-Commerce Shop Project

A robust e-commerce platform built with Django, featuring a modern shopping cart system, order management, and automated email notifications.

## 🌟 Features

### Shop Management
- Product catalog with categories
- Detailed product pages with images and descriptions
- Category-based product filtering
- Advanced product search capabilities
- Product availability tracking

### Shopping Cart
- Dynamic shopping cart functionality
- Real-time cart updates
- Persistent cart sessions
- Quantity management
- Total price calculations

### Order System
- Secure checkout process
- Order tracking
- Email notifications for orders
- Order history
- Payment status tracking

### User Experience
- Responsive design
- User-friendly interface
- Easy navigation between categories
- Detailed product information
- Streamlined checkout process

### Admin Features
- Product management
- Category management
- Order tracking
- Inventory management
- Sales monitoring

### Technical Features
- Celery task queue for asynchronous operations
- Email notification system
- Logging system for debugging and monitoring
- Secure payment processing
- Database optimization with proper indexing

## 🚀 Technology Stack

- **Backend**: Django
- **Task Queue**: Celery
- **Database**: SQLite (development)
- **Image Handling**: Django ImageField
- **Email**: SMTP (Gmail)
- **Logging**: Python's logging module



#### Product
- Category association
- Name, slug, image
- Description
- Price
- Availability status
- Creation and update timestamps

#### Order
- Customer information
- Shipping details
- Payment status
- Order items
- Total cost calculation

#### Cart
- Session-based shopping cart
- Product quantity management
- Price calculations
- Cart item management

## 📧 Email Notifications

The system sends professional email notifications for:
- Order confirmation
- Payment confirmation
- Shipping updates
- Order status changes

## 🔍 Logging

Comprehensive logging system for:
- Order processing
- Payment transactions
- Cart operations
- Product management
- Error tracking


Regular updates and maintenance are performed to:
- Keep dependencies up to date
- Fix bugs
- Add new features
- Improve performance
- Enhance security

## 🔐 Security

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password handling
- Protected admin interface

