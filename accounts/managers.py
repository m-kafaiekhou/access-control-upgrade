from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models


class OperatorManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def create_user(self, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        return self.create_user(password, **extra_fields)


class PersonalManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
