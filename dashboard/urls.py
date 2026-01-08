from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.home, name='home'),
    
    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/update/', views.sale_update, name='sale_update'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),
    
    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # Expenses
    path('expenses/', views.expenses_list, name='expenses_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    
    # Goals
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
]