from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Plan(models.TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    PREMIUM = 'premium', 'Premium'

class CustomUser(AbstractUser):
    plan = models.CharField(max_length=50, choices=Plan.choices, default=Plan.FREE)
    pages_used_this_month = models.IntegerField(default=0)
    quota_reset_at = models.DateTimeField(null=True, blank=True)

    QUOTA_MAP = {
            Plan.FREE: 50,
            Plan.PRO: 200,
            Plan.PREMIUM: 600,
        }

    def get_quota(self):
        return self.QUOTA_MAP.get(self.plan, 0)
            
        
        
