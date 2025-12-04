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

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="📚", help_text="Emoji or Icon class")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Course(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField(default=10, help_text="Cost in Creds")
    duration = models.CharField(max_length=50, default="4 Weeks", help_text="e.g. '4 Weeks', '10 Hours'")
    image = models.CharField(max_length=255, default="https://via.placeholder.com/300", help_text="URL to course image")
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField() # Positive for earn, negative for spend
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.amount} ({self.description})'

