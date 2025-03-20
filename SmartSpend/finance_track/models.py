from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    revolut_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    ai_analysis = models.OneToOneField("AIAnalysis", on_delete=models.SET_NULL, null=True, blank=True, related_name="expense_analysis")

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.category.name if self.category else 'Uncategorized'})"

class Income(models.Model):
    user = models.ForeignKey

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
class AIAnalysis(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name="analysis")
    ai_classification = models.CharField(max_length=255)  
    ai_tips = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"AI Analysis for {self.expense}"
