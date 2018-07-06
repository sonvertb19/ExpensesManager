from django.contrib import admin
from main.models import Expense, UserEmailConfirmation
# Register your models here.
admin.site.register(Expense)
admin.site.register(UserEmailConfirmation)