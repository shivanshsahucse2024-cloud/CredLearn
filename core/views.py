from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Course, User
from .forms import CustomUserCreationForm, CourseForm, ProfileUpdateForm

# --- Authentication ---

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Landing Page ---

def landing_page(request):
    return render(request, 'core/landing.html')

# --- Main Dashboard ---

@login_required
def dashboard(request):
    # Show all courses not taught by current user and not already enrolled
    available_courses = Course.objects.exclude(teacher=request.user).exclude(students=request.user)
    
    # Courses I am learning
    my_courses = request.user.enrolled_courses.all()
    
    # Courses I am teaching (if teacher)
    teaching_courses = request.user.teaching_courses.all()

    context = {
        'available_courses': available_courses,
        'my_courses': my_courses,
        'teaching_courses': teaching_courses,
    }
    return render(request, 'core/dashboard.html', context)

# --- Profile CRUD ---

@login_required
def profile_view(request):
    return render(request, 'core/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'core/profile_edit.html', {'form': form})

# --- Course Logic ---

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Course created! Earn creds when students join.")
            return redirect('dashboard')
    else:
        form = CourseForm()
    return render(request, 'core/course_form.html', {'form': form})

@login_required
def join_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user
    
    # Logic: Check if already enrolled
    if student in course.students.all():
        messages.info(request, "You are already in this course.")
        return redirect('dashboard')
        
    # Logic: Check Creds
    if student.creds >= course.price:
        # Transaction
        student.creds -= course.price
        course.teacher.creds += course.price
        
        student.save()
        course.teacher.save()
        
        course.students.add(student)
        messages.success(request, f"Successfully joined {course.title}!")
    else:
        messages.error(request, "Not enough Creds to join this course!")
        
    return redirect('dashboard')

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Security: Only teacher/owner can edit
    if request.user != course.teacher:
        messages.error(request, "You are not authorized to edit this course.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('dashboard')
    else:
        form = CourseForm(instance=course)
    
    # Reuse course_form.html but pass a flag or context if needed, 
    # or we can just let the template render the form with values.
    # To make the title say "Edit Course", we can pass a context variable.
    return render(request, 'core/course_form.html', {'form': form, 'is_edit': True})

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Security: Only teacher/owner can delete
    if request.user != course.teacher:
        messages.error(request, "You are not authorized to delete this course.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('dashboard')
        
    return render(request, 'core/course_confirm_delete.html', {'course': course})