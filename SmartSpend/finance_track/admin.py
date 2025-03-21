from django.contrib import admin
from .models import User, Transaction, Receipt, FinancialTip

admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Receipt)
admin.site.register(FinancialTip)
