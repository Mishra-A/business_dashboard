import os
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import Category, Product, Customer, Sale

def populate(user):
    # Categories
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Toys']
    cat_objects = []
    for cat in categories:
        obj, created = Category.objects.get_or_create(
            name=cat, user=user, defaults={'description': f'{cat} category'}
        )
        cat_objects.append(obj)
        print(f"✅ Category: {cat}")
    
    # Products
    products_data = [
        ('Laptop', 999.99, 700, 'Electronics', 50),
        ('Smartphone', 599.99, 400, 'Electronics', 100),
        ('T-Shirt', 29.99, 10, 'Clothing', 200),
        ('Jeans', 59.99, 30, 'Clothing', 150),
        ('Pizza', 15.99, 8, 'Food', 0),
        ('Novel', 19.99, 12, 'Books', 80),
        ('Action Figure', 24.99, 15, 'Toys', 60),
    ]
    
    product_objects = []
    for name, price, cost, cat_name, stock in products_data:
        cat = Category.objects.get(name=cat_name, user=user)
        obj, created = Product.objects.get_or_create(
            name=name, user=user,
            defaults={
                'price': Decimal(str(price)),
                'cost': Decimal(str(cost)),
                'category': cat,
                'stock_quantity': stock
            }
        )
        product_objects.append(obj)
        print(f"✅ Product: {name}")
    
    # Customers
    customers_data = [
        ('John Doe', 'john@example.com', '1234567890'),
        ('Jane Smith', 'jane@example.com', '0987654321'),
        ('Bob Johnson', 'bob@example.com', '1112223333'),
        ('Alice Brown', 'alice@example.com', '4445556666'),
        ('Charlie Wilson', 'charlie@example.com', '7778889999'),
    ]
    
    customer_objects = []
    for name, email, phone in customers_data:
        obj, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'name': name, 'phone': phone, 'user': user,
                'city': 'New York', 'country': 'USA'
            }
        )
        customer_objects.append(obj)
        print(f"✅ Customer: {name}")
    
    # Sales (30 transactions)
    print("\n📊 Creating sales...")
    for i in range(30):
        customer = random.choice(customer_objects)
        product = random.choice(product_objects)
        quantity = random.randint(1, 5)
        days_ago = random.randint(0, 60)
        sale_date = datetime.now().date() - timedelta(days=days_ago)
        
        last_invoice = Sale.objects.filter(user=user).order_by('-id').first()
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        invoice_number = f"{user.username.upper()}-INV-{next_num:05d}"
        
        Sale.objects.create(
            invoice_number=invoice_number,
            customer=customer,
            product=product,
            quantity=quantity,
            unit_price=product.price,
            discount=random.choice([0, 5, 10]),
            payment_method=random.choice(['cash', 'card', 'online']),
            status='completed',
            sale_date=sale_date,
            user=user
        )
    
    print(f"\n🎉 Success for {user.username}!")
    print(f"   📁 {len(cat_objects)} Categories")
    print(f"   📦 {len(product_objects)} Products")
    print(f"   👤 {len(customer_objects)} Customers")
    print(f"   💰 30 Sales")

if __name__ == '__main__':
    username = input("Enter username to populate data for: ")
    try:
        user = User.objects.get(username=username)
        populate(user)
    except User.DoesNotExist:
        print("❌ User not found. Please create the user first.")
