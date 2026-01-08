from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.emails import send_monthly_report

class Command(BaseCommand):
    help = 'Send monthly reports to all users'

    def handle(self, *args, **kwargs):
        users = User.objects.filter(is_active=True)
        
        for user in users:
            try:
                send_monthly_report(user)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Monthly report sent to {user.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to send report to {user.email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Finished sending monthly reports to {users.count()} users')
        )
