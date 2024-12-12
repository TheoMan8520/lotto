from django.contrib import admin
from app.models import Account
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class AccountInLine(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'
    list_display = ('user', 'banknumber', 'bankname')  # Fields to display in the admin list view
    search_fields = ('user__username', 'banknumber')

class CustomizedUserAdmin (UserAdmin):
    inlines = (AccountInLine, )
    
admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin )