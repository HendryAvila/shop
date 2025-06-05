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

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment
- Windows/Linux/Mac OS

## 🛠 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd shop
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file with the following variables
DJANGO_SECRET_KEY=your_secret_key
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## 🏃‍♂️ Running the Application

1. Start Celery worker (in a separate terminal):
```bash
celery -A core worker --pool=solo -l info
```

2. Access the application:
- Main site: http://localhost:8000
- Admin interface: http://localhost:8000/admin

## 📁 Project Structure

```
core/
├── cart/           # Shopping cart functionality
├── orders/         # Order management
├── products/       # Product catalog
├── shop/           # Main shop application
├── media/         # User-uploaded files
├── static/        # Static files
└── templates/     # HTML templates
```

## 🔧 Key Components

### Models

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

## 👥 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, email support@shop.com or create an issue in the repository.

## 🔄 Updates and Maintenance

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

## 🎯 Future Enhancements

- User authentication system
- Payment gateway integration
- Advanced search functionality
- Product reviews and ratings
- Wishlist functionality
- Multiple language support
- API development
- Mobile application