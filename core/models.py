from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model to handle roles and credits.
    """
    is_teacher = models.BooleanField(default=False, verbose_name="I want to Teach")
    creds = models.IntegerField(default=100) # Everyone starts with 100 creds
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

class Course(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_courses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField(default=10, help_text="Cost in Creds")
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title