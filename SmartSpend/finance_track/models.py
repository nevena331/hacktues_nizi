from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import EmailValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, validators=[EmailValidator("Enter a valid email address.")])
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=20, default="manual")

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.date.strftime('%Y-%m-%d')}"

class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receipts")
    image = models.ImageField(upload_to="receipts/")
    scanned_text = models.TextField(blank=True)
    predicted_category = models.CharField(max_length=50, blank=True)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_scanned = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Receipt for {self.user.email} on {self.date_scanned.strftime('%Y-%m-%d')}"

class FinancialTip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="financial_tips")
    tip_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    month = models.PositiveIntegerField(null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Tip for {self.user.email} on {self.created_at.strftime('%Y-%m-%d')}"
