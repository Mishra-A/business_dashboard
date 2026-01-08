from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import Sale, Product, Customer, Expense, Goal, Category
from .forms import SaleForm, ProductForm, CustomerForm, ExpenseForm, GoalForm, CategoryForm
import json
from .emails import send_sale_notification

@login_required
def home(request):
    """Main dashboard view with safe date handling (SQLite compatible)"""
    from collections import defaultdict
    user = request.user
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month = (start_of_month - timedelta(days=1)).replace(day=1)

    # Base metrics
    sales_qs = Sale.objects.filter(user=user, status='completed', sale_date__isnull=False)
    total_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales = sales_qs.count()
    total_customers = Customer.objects.filter(user=user).count()
    total_products = Product.objects.filter(user=user).count()

    month_sales_qs = sales_qs.filter(sale_date__gte=start_of_month)
    month_revenue = month_sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    month_sales = month_sales_qs.count()

    last_month_revenue = sales_qs.filter(
        sale_date__gte=last_month, sale_date__lt=start_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Growth
    revenue_growth = ((month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue else 0

    # Recent sales
    recent_sales = Sale.objects.filter(user=user).select_related('customer', 'product')[:5]

    # Top products
    top_products = sales_qs.values('product__name').annotate(
        total_quantity=Sum('quantity'), total_revenue=Sum('total_amount')
    ).order_by('-total_revenue')[:5]

    # -----------------------------
    # ✅ Fix: do date grouping manually in Python (no SQLite functions)
    # -----------------------------

    # Monthly revenue (last 6 months)
    six_months_ago = start_of_month - timedelta(days=180)
    monthly_sales = sales_qs.filter(sale_date__gte=six_months_ago)
    monthly_map = defaultdict(float)
    for sale in monthly_sales:
        month_key = sale.sale_date.strftime('%b %Y')
        monthly_map[month_key] += float(sale.total_amount)
    chart_labels = list(monthly_map.keys())
    chart_revenue = list(monthly_map.values())
    chart_sales_count = [sales_qs.filter(sale_date__month=sale.sale_date.month).count() for sale in monthly_sales[:len(chart_labels)]]

    # Daily revenue for current month
    daily_sales = sales_qs.filter(sale_date__gte=start_of_month)
    daily_map = defaultdict(float)
    for sale in daily_sales:
        day_key = sale.sale_date.strftime('%d %b')
        daily_map[day_key] += float(sale.total_amount)
    daily_labels = list(daily_map.keys())
    daily_revenue_data = list(daily_map.values())

    # Expenses and profit
    month_expenses = Expense.objects.filter(
        user=user, expense_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    net_profit = month_revenue - month_expenses

    # Active goals
    active_goals = Goal.objects.filter(user=user, end_date__gte=today).order_by('end_date')[:3]

    context = {
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_products': total_products,
        'month_revenue': month_revenue,
        'month_sales': month_sales,
        'month_expenses': month_expenses,
        'net_profit': net_profit,
        'revenue_growth': round(revenue_growth, 2),
        'recent_sales': recent_sales,
        'top_products': top_products,
        'active_goals': active_goals,
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue': json.dumps(chart_revenue),
        'chart_sales_count': json.dumps(chart_sales_count),
        'daily_labels': json.dumps(daily_labels),
        'daily_revenue_data': json.dumps(daily_revenue_data),
    }

    return render(request, 'dashboard/home.html', context)

    """Main dashboard view with statistics"""
    user = request.user
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month = (start_of_month - timedelta(days=1)).replace(day=1)

    # Total statistics
    total_revenue = Sale.objects.filter(user=user, status='completed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    total_sales = Sale.objects.filter(user=user, status='completed').count()
    total_customers = Customer.objects.filter(user=user).count()
    total_products = Product.objects.filter(user=user).count()

    # This month statistics
    month_revenue = Sale.objects.filter(
        user=user, status='completed', sale_date__gte=start_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    month_sales = Sale.objects.filter(
        user=user, status='completed', sale_date__gte=start_of_month
    ).count()

    # Last month statistics for comparison
    last_month_revenue = Sale.objects.filter(
        user=user, status='completed',
        sale_date__gte=last_month, sale_date__lt=start_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Calculate growth percentages
    revenue_growth = 0
    if last_month_revenue > 0:
        revenue_growth = ((month_revenue - last_month_revenue) / last_month_revenue) * 100

    # Recent sales
    recent_sales = Sale.objects.filter(user=user).select_related('customer', 'product')[:5]

    # Top products
    top_products = Sale.objects.filter(user=user, status='completed').values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_amount')
    ).order_by('-total_revenue')[:5]

    # Monthly revenue chart (last 6 months)
    six_months_ago = start_of_month - timedelta(days=180)
    monthly_data = Sale.objects.filter(
        user=user, status='completed',
        sale_date__isnull=False,
        sale_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('sale_date')
    ).values('month').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')

    chart_labels = [item['month'].strftime('%b %Y') for item in monthly_data if item['month']]
    chart_revenue = [float(item['revenue']) for item in monthly_data if item['month']]
    chart_sales_count = [item['count'] for item in monthly_data if item['month']]

    # Daily revenue for current month
    daily_revenue = Sale.objects.filter(
        user=user, status='completed',
        sale_date__isnull=False,
        sale_date__gte=start_of_month
    ).annotate(
        day=TruncDate('sale_date')
    ).values('day').annotate(
        revenue=Sum('total_amount')
    ).order_by('day')

    daily_labels = [item['day'].strftime('%d %b') for item in daily_revenue if item['day']]
    daily_revenue_data = [float(item['revenue']) for item in daily_revenue if item['day']]

    # Expenses this month
    month_expenses = Expense.objects.filter(
        user=user, expense_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Net profit
    net_profit = month_revenue - month_expenses

    # Active goals
    active_goals = Goal.objects.filter(
        user=user, end_date__gte=today
    ).order_by('end_date')[:3]

    context = {
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_products': total_products,
        'month_revenue': month_revenue,
        'month_sales': month_sales,
        'month_expenses': month_expenses,
        'net_profit': net_profit,
        'revenue_growth': round(revenue_growth, 2),
        'recent_sales': recent_sales,
        'top_products': top_products,
        'active_goals': active_goals,
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue': json.dumps(chart_revenue),
        'chart_sales_count': json.dumps(chart_sales_count),
        'daily_labels': json.dumps(daily_labels),
        'daily_revenue_data': json.dumps(daily_revenue_data),
    }

    return render(request, 'dashboard/home.html', context)

# ------------------ SALES CRUD ------------------ #

@login_required
def sales_list(request):
    sales = Sale.objects.filter(user=request.user).select_related('customer', 'product')

    # Filters
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status_filter:
        sales = sales.filter(status=status_filter)
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)

    return render(request, 'dashboard/sales_list.html', {
        'sales': sales,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def sale_create(request):
    """Create new sale"""
    if request.method == 'POST':
        form = SaleForm(request.POST, user=request.user)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            
            # Generate unique invoice number with retry logic
            max_attempts = 10
            for attempt in range(max_attempts):
                last_sale = Sale.objects.filter(user=request.user).order_by('-id').first()
                if last_sale and last_sale.invoice_number:
                    try:
                        last_number = int(last_sale.invoice_number.split('-')[-1])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                
                invoice_number = f"INV-{new_number:05d}"
                
                # Check if invoice number already exists
                if not Sale.objects.filter(invoice_number=invoice_number, user=request.user).exists():
                    sale.invoice_number = invoice_number
                    break
            else:
                # If all attempts failed, use timestamp-based number
                import time
                timestamp = int(time.time())
                sale.invoice_number = f"INV-{timestamp % 100000:05d}"
            
            try:
                sale.save()
                
                # Send email notification
                try:
                    from .emails import send_sale_notification
                    send_sale_notification(sale)
                    messages.success(request, f'Sale created successfully! Email notification sent to {request.user.email}.')
                except Exception as e:
                    messages.success(request, 'Sale created successfully!')
                    print(f"Email error: {e}")
                
                return redirect('dashboard:sales_list')
            except Exception as e:
                messages.error(request, f'Error creating sale: {str(e)}')
                print(f"Sale creation error: {e}")
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = SaleForm(user=request.user)
    
    return render(request, 'dashboard/sale_form.html', {'form': form, 'action': 'Create'})

@login_required
def sale_update(request, pk):
    sale = get_object_or_404(Sale, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully!')
            return redirect('dashboard:sales_list')
    else:
        form = SaleForm(instance=sale, user=request.user)

    return render(request, 'dashboard/sale_form.html', {'form': form, 'action': 'Update'})


@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk, user=request.user)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale deleted successfully!')
        return redirect('dashboard:sales_list')
    return render(request, 'dashboard/sale_confirm_delete.html', {'sale': sale})


# ------------------ CUSTOMERS ------------------ #

@login_required
def customers_list(request):
    """List all customers safely"""
    customers = Customer.objects.filter(user=request.user).annotate(
        total_purchases_count=Count('sales'),
        total_spent_amount=Sum('sales__total_amount')
    )

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'dashboard/customers_list.html', context)



@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('dashboard:customers_list')
    else:
        form = CustomerForm()

    return render(request, 'dashboard/customer_form.html', {'form': form, 'action': 'Add'})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('dashboard:customers_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'dashboard/customer_form.html', {'form': form, 'action': 'Update'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('dashboard:customers_list')
    return render(request, 'dashboard/customer_confirm_delete.html', {'customer': customer})


# ------------------ PRODUCTS ------------------ #

@login_required
def products_list(request):
    products = Product.objects.filter(user=request.user).select_related('category')
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    categories = Category.objects.filter(user=request.user)
    return render(request, 'dashboard/products_list.html', {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('dashboard:products_list')
    else:
        form = ProductForm(user=request.user)
    return render(request, 'dashboard/product_form.html', {'form': form, 'action': 'Add'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard:products_list')
    else:
        form = ProductForm(instance=product, user=request.user)
    return render(request, 'dashboard/product_form.html', {'form': form, 'action': 'Update'})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('dashboard:products_list')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


# ------------------ ANALYTICS ------------------ #

@login_required
def analytics(request):
    user = request.user
    today = timezone.now().date()
    date_from = request.GET.get('date_from', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', today.strftime('%Y-%m-%d'))

    sales = Sale.objects.filter(
        user=user, status='completed',
        sale_date__isnull=False,
        sale_date__gte=date_from, sale_date__lte=date_to
    )

    total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_profit = sum([sale.profit for sale in sales])

    category_sales = sales.values('product__category__name').annotate(
        total=Sum('total_amount')
    ).order_by('-total')

    category_labels = [item['product__category__name'] or 'Uncategorized' for item in category_sales]
    category_data = [float(item['total']) for item in category_sales]

    payment_sales = sales.values('payment_method').annotate(count=Count('id')).order_by('-count')
    payment_labels = [dict(Sale.PAYMENT_METHOD).get(item['payment_method'], item['payment_method'])
                      for item in payment_sales]
    payment_data = [item['count'] for item in payment_sales]

    top_customers = Customer.objects.filter(user=user).annotate(
        total_spent=Sum('sales__total_amount', filter=Q(sales__status='completed'))
    ).order_by('-total_spent')[:10]

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'top_customers': top_customers,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'payment_labels': json.dumps(payment_labels),
        'payment_data': json.dumps(payment_data),
    }
    return render(request, 'dashboard/analytics.html', context)


# ------------------ EXPENSES ------------------ #

@login_required
def expenses_list(request):
    expenses = Expense.objects.filter(user=request.user)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'dashboard/expenses_list.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
    })


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('dashboard:expenses_list')
    else:
        form = ExpenseForm()
    return render(request, 'dashboard/expense_form.html', {'form': form, 'action': 'Add'})


# ------------------ GOALS ------------------ #

@login_required
def goals_list(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'dashboard/goals_list.html', {'goals': goals})


@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal created successfully!')
            return redirect('dashboard:goals_list')
    else:
        form = GoalForm()
    return render(request, 'dashboard/goal_form.html', {'form': form, 'action': 'Create'})
