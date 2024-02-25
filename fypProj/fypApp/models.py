from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.save(using=self._db)
        user.password = password  # Set the password directly without hashing
        user.save(using=self._db)  # Save again after setting the password
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('userType', 1)
        user = self.create_user(email, username, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
class Users(AbstractBaseUser, PermissionsMixin):
    userId = models.AutoField(primary_key=True)
    userType = models.PositiveIntegerField()
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    contactNumber = models.CharField(max_length=15)
    isOrganisation = models.BooleanField(default=False)
    isApprovedOrganisation = models.BooleanField(default=False)
    rejectionReason = models.TextField(null=True, default='', blank=True)
    hasBeenUpdated = models.BooleanField(default=False)
    isNewUser = models.BooleanField(default=False)
    reviewDate = models.DateField(null=True, blank=True) 

    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False) 

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
class Activities(models.Model):
    activityId = models.AutoField(primary_key=True)
    organisationId = models.ForeignKey(Users, on_delete=models.CASCADE, limit_choices_to={'isOrganisation': True})
    title = models.CharField(max_length=255)
    description = models.TextField()
    activityImage1 = models.ImageField(upload_to='activity_images/', null=True, blank=True)
    activityImage2 = models.ImageField(upload_to='activity_images/', null=True, blank=True)
    activityImage3 = models.ImageField(upload_to='activity_images/', null=True, blank=True)
    activityType = models.CharField(max_length=50)
    maximumSignups = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class UserHasActivities(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)
    isLiked = models.BooleanField(default=False)
    isSignup = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.activity.title}"
    
class UserHasOrganisation(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_has_organisations', limit_choices_to={'isOrganisation': False})
    organisation = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='organisation_has_organisations', limit_choices_to={'isOrganisation': True})
    donations = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    complain = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.organisation.username}"
    
class OrganisationDetails(models.Model):
    organisationId = models.ForeignKey(Users, on_delete=models.CASCADE)
    organisationName = models.CharField(max_length=255)
    organisationFocus = models.TextField()
    organisationShortDescription = models.TextField()
    organisationLongDescription = models.TextField()
    organisationImage1 = models.ImageField(upload_to='organisation_images/', null=True, blank=True)
    organisationImage2 = models.ImageField(upload_to='organisation_images/', null=True, blank=True)
    organisationImage3 = models.ImageField(upload_to='organisation_images/', null=True, blank=True)
    acceptQrDonations = models.BooleanField(default=False)
    paidToDate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.organisationName