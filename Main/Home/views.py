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
