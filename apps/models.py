from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import CharField, Model, DecimalField, ForeignKey, CASCADE, TextField, TextChoices, SET_NULL, \
    DateTimeField, EmailField


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email topilmadi")
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    first_name = None
    last_name = None
    fullname = CharField(max_length=128)
    email = EmailField(("email address"), unique=True)


class Category(Model):
    class TypeChoices(TextChoices):
        income = 'income', "Income"
        expense = 'expense', "Expense"
    name = CharField(max_length=50, unique=True)
    icon= CharField(max_length=255)
    type=CharField(max_length=50, choices=TypeChoices.choices)
    def __str__(self):
        return self.name

class Expense(Model):
    class TypeChoices(TextChoices):
        income = 'income', "Income"
        expense = 'expense', "Expense"

    amount = DecimalField(max_digits=10, decimal_places=2)
    type = CharField(max_length=50,choices=TypeChoices.choices)
    description = TextField()
    category=ForeignKey(Category,on_delete=SET_NULL,null=True,blank=True)
    created_at=DateTimeField(auto_now_add=True)
    user=ForeignKey(User,on_delete=SET_NULL,null=True, blank=True)





