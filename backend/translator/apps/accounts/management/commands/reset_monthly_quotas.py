from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from django.utils import timezone
from datetime import datetime



class Command(BaseCommand):
    help = 'Reset monthly page quotas for all users'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        if today.month == 12:
            next_reset = timezone.make_aware(datetime(today.year + 1, 1,1))
        else:
            next_reset = timezone.make_aware(datetime(today.year, today.month+1, 1))

        CustomUser.objects.update(pages_used_this_month=0, quota_reset_at=next_reset)
        self.stdout.write(self.style.SUCCESS('Quota Reset Successfully'))
        
        
        