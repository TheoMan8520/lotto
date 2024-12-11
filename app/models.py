from django.conf import settings
from django.db import models


class Room(models.Model):
    is_open = models.BooleanField(default=True)
    shares = models.IntegerField()
    
    def __str__(self):
        return self.id

class Round(models.Model):
    date = models.DateField()
    
    def __str__(self):
        return self.id

class Transaction(models.Model):
    lotto = models.CharField(max_length=3)
    share = models.IntegerField()
    status = models.CharField(max_length=255, default="รอการยืนยันการชำระเงิน")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='transactions')
    round_bought = models.ForeignKey(Round, default=None, on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return self.id

class LottoBought(models.Model):
    lotto = models.CharField(max_length=6)
    prices = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='lottos')
    round_bought = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='lottos')
    
    def __str__(self):
        return self.id

