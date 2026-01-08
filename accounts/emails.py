from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = f'Welcome to Business Dashboard, {user.first_name}!'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4F46E5; text-align: center;">Welcome to Business Dashboard! 🎉</h2>
                
                <p>Hi <strong>{user.first_name}</strong>,</p>
                
                <p>Thank you for signing up! We're excited to have you on board.</p>
                
                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #4F46E5; margin-top: 0;">Getting Started:</h3>
                    <ul>
                        <li>📦 Add your products and categories</li>
                        <li>👥 Create customer profiles</li>
                        <li>💰 Record your first sale</li>
                        <li>📊 View analytics and reports</li>
                    </ul>
                </div>
                
                <p>If you have any questions, feel free to reach out to our support team.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Business Dashboard Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666; text-align: center;">
                    This is an automated message. Please do not reply to this email.
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

def send_password_reset_email(user, reset_link):
    """Send password reset email"""
    subject = 'Reset Your Password - Business Dashboard'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4F46E5; text-align: center;">Password Reset Request 🔐</h2>
                
                <p>Hi <strong>{user.first_name}</strong>,</p>
                
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p style="color: #EF4444; font-weight: bold;">⚠️ This link will expire in 24 hours.</p>
                
                <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Business Dashboard Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    If the button doesn't work, copy and paste this link:<br>
                    <a href="{reset_link}" style="color: #4F46E5;">{reset_link}</a>
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