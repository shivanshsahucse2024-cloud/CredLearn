from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Course

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'bio')

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'duration', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'linkedin_profile_url', 'skills', 'experience', 'education', 'certification']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'linkedin_profile_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.linkedin.com/in/yourname'}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Python\nDjango\nReact', 'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'education': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'certification': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }