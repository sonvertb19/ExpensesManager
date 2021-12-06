from django.contrib import admin
from main.models import Expense, UserEmailConfirmation, Group, Account, Category
# Register your models here.
admin.site.register(Expense)
admin.site.register(UserEmailConfirmation)
admin.site.register(Group)
admin.site.register(Account)
admin.site.register(Category)
