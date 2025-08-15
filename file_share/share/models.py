from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import pickle


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name


class SharedFile(models.Model):
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)  # For external URLs
    file_name = models.CharField(max_length=255)
    file_size = models.CharField(max_length=50, blank=True)
    shared_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    share_type = models.CharField(max_length=50)
    share_time = models.DateTimeField(default=timezone.now)
    share_expiry = models.DateTimeField(blank=True, null=True)
    file_type = models.CharField(max_length=50)
    shared_to = models.JSONField(default=list)
    file_description = models.TextField(blank=True, null=True)

    feature_vector = models.BinaryField(
        null=True,
        blank=True,
        help_text="Serialized feature vector for AI tasks (e.g., similarity search)."
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional metadata about the file (e.g., tags, AI-generated insights)."
    )

    def save_feature_vector(self, feature_vector):
        self.feature_vector = pickle.dumps(feature_vector)
        self.save()

    def get_feature_vector(self):
        return pickle.loads(self.feature_vector) if self.feature_vector else None

    def get_file_url(self):
        """Return the appropriate file URL (uploaded file or external URL)"""
        if self.file:
            # Return protected URL for uploaded files
            return f'/protected-media/{self.file.name}'
        return self.file_url
    
    def get_protected_url(self):
        """Return the protected URL for the file"""
        if self.file:
            return f'/protected-media/{self.file.name}'
        return self.file_url

    def __str__(self):
        return self.file_name