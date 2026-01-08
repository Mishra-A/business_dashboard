from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        if self.price > 0:
            return ((self.price - self.cost) / self.price) * 100
        return 0

class Customer(models.Model):
    CUSTOMER_TYPE = [
        ('new', 'New'),
        ('returning', 'Returning'),
        ('vip', 'VIP'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE, default='new')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def total_purchases(self):
        return self.sales.aggregate(total=models.Sum('total_amount'))['total'] or 0

class Sale(models.Model):
    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment'),
        ('bank', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    sale_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sale_date', '-created_at']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"
    
    def save(self, *args, **kwargs):
        from decimal import Decimal  # ✅ Import Decimal here
        # Calculate total amount
        subtotal = self.unit_price * self.quantity
        discount_amount = subtotal * (Decimal(self.discount) / Decimal(100))  # ✅ Fixed here
        self.total_amount = subtotal - discount_amount
        super().save(*args, **kwargs)
    
    @property
    def profit(self):
        return (self.unit_price - self.product.cost) * self.quantity

class Expense(models.Model):
    EXPENSE_TYPE = [
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('utilities', 'Utilities'),
        ('marketing', 'Marketing'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE)
    expense_date = models.DateField()
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - ${self.amount}"

class Goal(models.Model):
    GOAL_TYPE = [
        ('revenue', 'Revenue'),
        ('sales', 'Sales'),
        ('customers', 'Customers'),
        ('profit', 'Profit'),
    ]
    
    PERIOD = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    title = models.CharField(max_length=200)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    period = models.CharField(max_length=20, choices=PERIOD)
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)
        return 0
    
    @property
    def is_achieved(self):
        return self.current_amount >= self.target_amount