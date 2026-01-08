from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.db.models import Sum, Count
from datetime import datetime, timedelta

def send_sale_notification(sale):
    """Send email notification when a sale is created"""
    subject = f'New Sale Created - Invoice #{sale.invoice_number}'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #10B981; text-align: center;">✅ New Sale Recorded!</h2>
                
                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #4F46E5; margin-top: 0;">Sale Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Invoice Number:</td>
                            <td style="padding: 8px;">{sale.invoice_number}</td>
                        </tr>
                        <tr style="background-color: white;">
                            <td style="padding: 8px; font-weight: bold;">Customer:</td>
                            <td style="padding: 8px;">{sale.customer.name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Product:</td>
                            <td style="padding: 8px;">{sale.product.name}</td>
                        </tr>
                        <tr style="background-color: white;">
                            <td style="padding: 8px; font-weight: bold;">Quantity:</td>
                            <td style="padding: 8px;">{sale.quantity}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Unit Price:</td>
                            <td style="padding: 8px;">₹{sale.unit_price}</td>
                        </tr>
                        <tr style="background-color: white;">
                            <td style="padding: 8px; font-weight: bold;">Total Amount:</td>
                            <td style="padding: 8px; font-size: 18px; color: #10B981;"><strong>₹{sale.total_amount}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Payment Method:</td>
                            <td style="padding: 8px;">{sale.get_payment_method_display()}</td>
                        </tr>
                        <tr style="background-color: white;">
                            <td style="padding: 8px; font-weight: bold;">Date:</td>
                            <td style="padding: 8px;">{sale.sale_date.strftime('%B %d, %Y')}</td>
                        </tr>
                    </table>
                </div>
                
                {f'<p style="background-color: #FEF3C7; padding: 10px; border-radius: 5px;"><strong>Note:</strong> {sale.notes}</p>' if sale.notes else ''}
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Business Dashboard</strong>
                </p>
            </div>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [sale.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_weekly_report(user):
    """Send weekly performance report"""
    from .models import Sale, Customer, Product
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # Calculate statistics
    weekly_sales = Sale.objects.filter(
        user=user, 
        status='completed',
        sale_date__gte=week_ago,
        sale_date__lte=today
    )
    
    total_revenue = weekly_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales_count = weekly_sales.count()
    new_customers = Customer.objects.filter(user=user, created_at__gte=week_ago).count()
    
    subject = f'Weekly Report - {week_ago.strftime("%b %d")} to {today.strftime("%b %d, %Y")}'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4F46E5; text-align: center;">📊 Weekly Performance Report</h2>
                
                <p>Hi <strong>{user.first_name}</strong>,</p>
                
                <p>Here's your business performance for the past week:</p>
                
                <div style="background-color: #F3F4F6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div style="background-color: white; padding: 15px; border-radius: 5px; text-align: center;">
                            <div style="color: #6B7280; font-size: 14px;">Total Revenue</div>
                            <div style="color: #10B981; font-size: 24px; font-weight: bold;">₹{total_revenue:,.2f}</div>
                        </div>
                        <div style="background-color: white; padding: 15px; border-radius: 5px; text-align: center;">
                            <div style="color: #6B7280; font-size: 14px;">Total Sales</div>
                            <div style="color: #4F46E5; font-size: 24px; font-weight: bold;">{total_sales_count}</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <div style="background-color: white; padding: 15px; border-radius: 5px; text-align: center;">
                            <div style="color: #6B7280; font-size: 14px;">New Customers</div>
                            <div style="color: #F59E0B; font-size: 24px; font-weight: bold;">{new_customers}</div>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:8000/analytics/" 
                       style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Full Analytics
                    </a>
                </div>
                
                <p style="margin-top: 30px;">
                    Keep up the great work!<br>
                    <strong>Business Dashboard Team</strong>
                </p>
            </div>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_monthly_report(user):
    """Send monthly performance report"""
    from .models import Sale, Expense
    from datetime import datetime
    
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    
    # Calculate statistics
    monthly_sales = Sale.objects.filter(
        user=user,
        status='completed',
        sale_date__gte=start_of_month,
        sale_date__lte=today
    )
    
    total_revenue = monthly_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales_count = monthly_sales.count()
    total_expenses = Expense.objects.filter(
        user=user,
        expense_date__gte=start_of_month,
        expense_date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    net_profit = total_revenue - total_expenses
    
    subject = f'Monthly Report - {today.strftime("%B %Y")}'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4F46E5; text-align: center;">📈 Monthly Performance Report</h2>
                
                <p>Hi <strong>{user.first_name}</strong>,</p>
                
                <p>Here's your business summary for <strong>{today.strftime("%B %Y")}</strong>:</p>
                
                <div style="background-color: #F3F4F6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin-bottom: 15px; text-align: center;">
                        <div style="color: #6B7280; font-size: 14px;">Total Revenue</div>
                        <div style="color: #10B981; font-size: 28px; font-weight: bold;">₹{total_revenue:,.2f}</div>
                    </div>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin-bottom: 15px; text-align: center;">
                        <div style="color: #6B7280; font-size: 14px;">Total Expenses</div>
                        <div style="color: #EF4444; font-size: 28px; font-weight: bold;">₹{total_expenses:,.2f}</div>
                    </div>
                    
                    <div style="background-color: {'#D1FAE5' if net_profit >= 0 else '#FEE2E2'}; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="color: #6B7280; font-size: 14px;">Net Profit</div>
                        <div style="color: {'#10B981' if net_profit >= 0 else '#EF4444'}; font-size: 32px; font-weight: bold;">
                            ₹{net_profit:,.2f}
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px; background-color: white; padding: 15px; border-radius: 5px; text-align: center;">
                        <div style="color: #6B7280; font-size: 14px;">Total Sales</div>
                        <div style="color: #4F46E5; font-size: 24px; font-weight: bold;">{total_sales_count}</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:8000/" 
                       style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Dashboard
                    </a>
                </div>
                
                <p style="margin-top: 30px;">
                    Great work this month!<br>
                    <strong>Business Dashboard Team</strong>
                </p>
            </div>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )