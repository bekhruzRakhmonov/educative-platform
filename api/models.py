from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext as _

import uuid


class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, name, password=None, **others):
        others.setdefault('is_staff', True)
        others.setdefault('is_superuser', True)
        others.setdefault('is_active', True)

        if others.get('is_staff') is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        if others.get('is_superuser') is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")

        user = self.create_user(email, name, password, **others)
        # user.is_admin = True
        user.save(using=self._db)

        return user

    def create_user(self, email, name, password=None, **others):
        others.setdefault('is_active', True)
        if not email:
            raise ValueError("You must provide an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **others)
        user.set_password(password)
        user.save(using=self._db)

        return user


STATUS = (
    ("teacher", "TEACHER"),
    ("student", "STUDENT"),
)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"),max_length=200)
    email = models.EmailField(_("Email"), unique=True)
    status = models.CharField(_("Your status"), max_length=255, choices=STATUS)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "status"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Course(models.Model):
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="teacher")
    courses = models.ManyToManyField("ChildCourse", related_name="courses")


class ChildCourse(models.Model):
    name = models.CharField(_("Course name"), max_length=255)
    students = models.ManyToManyField(
        User, related_name="student")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
