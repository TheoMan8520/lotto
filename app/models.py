from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
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
    prize = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='lottos')
    round_bought = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='lottos')
    
    def __str__(self):
        return self.id

class Slip(models.Model):
    prize = models.IntegerField()
    status = models.CharField(max_length=255, default="กำลังดำเนินการ")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='slips')
    round_bought = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='slips')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='slips')
    
    def __str__(self):
        return self.id

class Account(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account')
    banknumber = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(10), MaxLengthValidator(10)],
    )
    bankname = models.CharField(
        max_length=50,  # Limit the length of bank name string
        choices=[
            ('ธนาคารกรุงเทพ', 'Bangkok Bank'),
            ('ธนาคารกสิกรไทย', 'Kasikorn Bank'),
            ('ธนาคารไทยพาณิชย์', 'Siam Commercial Bank'),
            ('ธนาคารกรุงไทย', 'Krung Thai Bank'),
            ('ธนาคารทหารไทยธนชาต', 'TMB Bank'),
            ('ธนาคารออมสิน', 'Government Savings Bank'),
            ('ยูโอบี ประเทศไทย', 'UOB Thailand'),
            ('ซิตี้แบงก์ ประเทศไทย', 'CitiBank Thailand'),
        ],
    )
    
    def __str__(self):
        return self.banknumber