from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    revolut_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null=True, blank=True)  
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.category.name if self.category else 'Uncategorized'})"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
class AIAnalysis(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name="analysis", null=True, blank=True)
    ai_classification = models.CharField(max_length=255, null=True, blank=True)  
    ai_tips = models.TextField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"AI Analysis for {self.expense}"
