<<<<<<< HEAD
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    lotto = models.CharField(max_length=3)
    share = models.IntegerField()
    status = models.CharField(max_length=255, default="รอการยืนยันการชำระเงิน")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class Account(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
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
        return self.user.username
=======
from django.db import models

# Create your models here.
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
