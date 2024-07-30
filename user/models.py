from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
    

# Create your models here.
class User(AbstractUser):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("active", "active"),
        ("inactive", "inactive"),
    )
    username = models.CharField(max_length=60)
    first_name = models.CharField(max_length=100,default="")
    last_name = models.CharField(max_length=100, default="")
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(default='profile_pictures/default_profile_image.png', upload_to='profile_pictures/')
    otp = models.IntegerField(null=True)
    bio=models.TextField(max_length=1000,default="")
    phone = models.CharField(max_length=15, null=True)
    is_active = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    objects=UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table='user'
        ordering=['id']
        
    
    