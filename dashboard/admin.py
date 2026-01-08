from django.contrib import admin

# Register your models here.

from .models import Category, Product, Customer, Sale, Expense, Goal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'cost', 'stock_quantity', 'user', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock_quantity']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'country', 'customer_type', 'created_at']
    list_filter = ['customer_type', 'country', 'city', 'created_at']
    search_fields = ['name', 'email', 'phone']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'product', 'quantity', 'total_amount', 
                   'payment_method', 'status', 'sale_date']
    list_filter = ['status', 'payment_method', 'sale_date']
    search_fields = ['invoice_number', 'customer__name', 'product__name']
    readonly_fields = ['total_amount']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'expense_type', 'expense_date', 'user']
    list_filter = ['expense_type', 'expense_date']
    search_fields = ['title', 'description']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal_type', 'target_amount', 'current_amount', 
                   'progress_percentage', 'period', 'end_date']
    list_filter = ['goal_type', 'period']
    search_fields = ['title']
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage:.1f}%"
    progress_percentage.short_description = 'Progress'