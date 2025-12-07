from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Home.models import Profile, Video, VideoView

# Create your views here.
#def index(request):
    #return HttpResponse( 'This is homepage of Teach and Earn platform' )
    
def home(request):
    return render(request,'index.html')

def Explore(request):
    return render( request,'explore.html' )

def about(request):
    return render(request,'about.html' )

def contact(request):
    return render(request,'contact.html' )

def services(request):
    return render(request,'services.html' )

def programming(request):
    return render(request,'programming.html')

def Design(request):
    return render(request,'Design.html')

def Music(request):
    return render(request,'music.html')

def Lang(request):
    return render(request,'Lang.html')

def mentor(request):
    return render(request,'mentor.html')

def mentors_available(request):
    mentors = [
        {'name': 'Riya Sharma', 'skill': 'HTML, CSS', 'status': 'Available', 'credits': 60},
        {'name': 'Aman Verma', 'skill': 'CSS, Animations', 'status': 'Busy', 'credits': 75},
        {'name': 'Aditya Rao', 'skill': 'Python, Django', 'status': 'Available', 'credits': 85},
        {'name': 'Sneha Patel', 'skill': 'React, JS', 'status': 'Offline', 'credits': 90},
    ]
    return render(request, 'mentors_available.html', {'mentors': mentors})

@login_required
def wallet(request):
    profile = request.user.profile

    # Credits earned (from uploads)
    uploads = Video.objects.filter(owner=request.user)

    # Credits spent (from watching others)
    spent = VideoView.objects.filter(viewer=request.user).exclude(video__owner=request.user)

    context = {
        "profile": profile,
        "uploads": uploads,
        "spent": spent
    }
    return render(request, "wallet.html", context)

def wallet(request):
    user = request.user

    profile, created = Profile.objects.get_or_create(user=user)

    return render(request, 'wallet.html', {'profile': profile})
