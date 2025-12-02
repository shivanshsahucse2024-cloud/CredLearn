from django.shortcuts import render

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


