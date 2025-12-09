from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Course, User, Transaction, Category, TimeSlot
from .forms import CustomUserCreationForm, CourseForm, ProfileUpdateForm
import json
from django.utils.dateparse import parse_datetime
from django.utils import timezone

# --- Authentication ---

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
            user = form.save()
            
            # Sync text skills to Skill model
            if user.skills:
                skill_names = [s.strip() for s in user.skills.split('\n') if s.strip()]
                # content retention strategy: verifying existing skills
                # 1. Get existing skills
                existing_skills = Skill.objects.filter(user=user)
                existing_names = set(s.name for s in existing_skills)
                new_names = set(skill_names)
                
                # Delete skills that are no longer in the list (optional, but good for consistency)
                # But be careful not to delete verified skills if user just made a typo? 
                # For now, strict sync:
                to_delete = existing_names - new_names
                Skill.objects.filter(user=user, name__in=to_delete).delete()
                
                # Create new skills
                for name in new_names:
                    Skill.objects.get_or_create(user=user, name=name)
            else:
                 # If empty, delete all?
                 Skill.objects.filter(user=user).delete()
                 
            messages.success(request, "Profile updated!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'core/profile_edit.html', {'form': form})

from .models import Skill
from .utils.gemini_utils import generate_quiz_questions, grade_quiz_answers

@login_required
def start_verification(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    
    # Generate questions
    try:
        questions = generate_quiz_questions(skill.name)
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('profile')
        
    if not questions:
        messages.error(request, "Could not generate quiz. Empty response from AI.")
        return redirect('profile')
        
    # Store in session
    request.session[f'quiz_{skill.id}'] = questions
    
    return render(request, 'core/quiz.html', {'skill': skill, 'questions': questions})

@login_required
def submit_verification(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)
    
    if request.method == 'POST':
        questions = request.session.get(f'quiz_{skill.id}')
        if not questions:
             messages.error(request, "Session expired. Please start over.")
             return redirect('profile')
             
        user_answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                q_id = key.split('_')[1]
                user_answers[q_id] = value
                
        # Grade
        grading_data = grade_quiz_answers(skill.name, questions, user_answers)
        
        # Handle backward compatibility or failure
        if isinstance(grading_data, int):
            score = grading_data
            detailed_results = []
        else:
            raw_score = grading_data.get('score', 0)
            try:
                # Handle edge case where score might be returned as a dict or string
                if isinstance(raw_score, dict):
                    # Try to find a numeric value if possible, or just fail
                    raw_score = raw_score.get('value', 0)
                score = int(raw_score)
            except (ValueError, TypeError):
                score = 0
            detailed_results = grading_data.get('results', [])
        
        # Merge user answers into detailed results for display
        # We need to match question_id from results with question text and user answer
        final_results = []
        questions_map = {str(q['id']): q['question'] for q in questions}
        
        for res in detailed_results:
            q_id = str(res.get('question_id'))
            
            # Normalize status
            status = res.get('status', '').lower()
            
            final_results.append({
                'question': questions_map.get(q_id, 'Unknown Question'),
                'user_answer': user_answers.get(q_id, '-'),
                'status': status,
                'correct_answer': res.get('correct_answer')
            })
            
        # If grading failed completely (empty results), we might want to fill basics
        if not final_results and score == 0:
             # Fallback if AI didn't return list
             pass

        passed = score >= 7
        if passed:
            skill.is_verified = True
            skill.save()
            messages.success(request, f"Congratulations! You passed the verification for {skill.name} with score {score}/10.")
        else:
            messages.warning(request, f"You scored {score}/10. You need 7 to pass. Review your results below.")
            
        # Clear session
        del request.session[f'quiz_{skill.id}']
        
        return render(request, 'core/quiz_result.html', {
            'skill': skill, 
            'score': score, 
            'passed': passed,
            'results': final_results
        })
    
    return redirect('profile')

# --- Course Logic ---

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            
            # Handle Time Slots
            slots_json = request.POST.get('slots_json')
            if slots_json:
                try:
                    slots_data = json.loads(slots_json)
                    for slot in slots_data:
                        start = parse_datetime(slot['start'])
                        end = parse_datetime(slot['end'])
                        if start and end:
                            TimeSlot.objects.create(
                                course=course,
                                start_time=start,
                                end_time=end
                            )
                except json.JSONDecodeError:
                    pass # Handle error gracefully or log it

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

        # Create Transaction Records
        Transaction.objects.create(
            user=student,
            amount=-course.price,
            description=f"Joined course: {course.title}",
            course=course
        )
        Transaction.objects.create(
            user=course.teacher,
            amount=course.price,
            description=f"Student joined course: {course.title}",
            course=course
        )
        
        course.students.add(student)
        messages.success(request, f"Successfully joined {course.title}!")
    else:
        messages.error(request, "Not enough Creds to join this course!")
        
    return redirect('dashboard')

@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    course = slot.course
    student = request.user
    
    if slot.is_booked:
        messages.error(request, "This slot is already booked.")
        return redirect('course_detail', course_id=course.id)

    if student.creds >= course.price:
        student.creds -= course.price
        course.teacher.creds += course.price
        student.save()
        course.teacher.save()
        
        slot.is_booked = True
        slot.booked_by = student
        slot.save()
        
        # Ensure student is in course list too
        if student not in course.students.all():
            course.students.add(student)

        Transaction.objects.create(
            user=student, 
            amount=-course.price, 
            description=f"Booked session for {course.title}", 
            course=course
        )
        Transaction.objects.create(
            user=course.teacher, 
            amount=course.price, 
            description=f"Student booked session: {course.title}", 
            course=course
        )
        
        messages.success(request, f"Successfully booked session at {slot.start_time.strftime('%Y-%m-%d %H:%M')}!")
    else:
        messages.error(request, "Not enough Creds to book this session!")

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

@login_required
def wallet(request):
    transactions = request.user.transactions.all().order_by('-timestamp')
    earned = transactions.filter(amount__gt=0)
    spent = transactions.filter(amount__lt=0)
    
    return render(request, 'core/wallet.html', {
        'profile': request.user,
        'uploads': earned,
        'spent': spent
    })


# --- Discovery Flow ---

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})

@login_required
def course_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    courses = Course.objects.filter(category=category)
    return render(request, 'core/course_list.html', {'category': category, 'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = request.user in course.students.all()
    slots = course.slots.filter(is_booked=False).order_by('start_time')
    return render(request, 'core/course_detail.html', {'course': course, 'is_enrolled': is_enrolled, 'slots': slots})

# --- Enhanced Dashboards ---

@login_required
def my_learning(request):
    my_courses = request.user.enrolled_courses.all()
    return render(request, 'core/my_learning.html', {'courses': my_courses})

@login_required
def my_teaching(request):
    teaching_courses = request.user.teaching_courses.all()
    return render(request, 'core/my_teaching.html', {'courses': teaching_courses})

@login_required
def course_dashboard_student(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user not in course.students.all():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course.id)
    
    # Get booked slots
    booked_slots = course.slots.filter(booked_by=request.user).order_by('start_time')
    
    # Check for active slot
    now = timezone.now()
    active_slot = None
    for slot in booked_slots:
        if slot.start_time <= now <= slot.end_time:
            active_slot = slot
            break
            
    return render(request, 'core/course_dashboard_student.html', {
        'course': course,
        'booked_slots': booked_slots,
        'active_slot': active_slot,
        'now': now # For debugging or UI logic
    })

@login_required
def course_dashboard_teacher(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher:
        messages.error(request, "You are not the teacher of this course.")
        return redirect('dashboard')
        
    slots = course.slots.all().order_by('start_time')
    
    # Check for active slot
    now = timezone.now()
    active_slot = None
    # We want to find if ANY booked slot is active right now
    for slot in slots:
        if slot.is_booked and slot.start_time <= now <= slot.end_time:
            active_slot = slot
            break
            
    return render(request, 'core/course_dashboard_teacher.html', {
        'course': course,
        'slots': slots,
        'active_slot': active_slot,
        'now': now
    })

def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    teaching_courses = profile_user.teaching_courses.all()
    # Calculate stats
    total_students = sum(c.students.count() for c in teaching_courses)
    
    return render(request, 'core/public_profile.html', {
        'profile_user': profile_user,
        'courses': teaching_courses,
        'total_students': total_students
    })

