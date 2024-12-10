from django.conf import settings
from django.db import models


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    lotto = models.CharField(max_length=3)
    share = models.IntegerField()
    status = models.CharField(max_length=255, default="รอการยืนยันการชำระเงิน")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id