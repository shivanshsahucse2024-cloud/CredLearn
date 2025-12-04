from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

from Home.models import Profile, LiveSession, SessionAttendance
from django.contrib.auth import logout


# ==========================================================
# BASIC PAGES
# ==========================================================
def home(request):
    return render(request, 'index.html')

def Explore(request):
    return render(request, 'explore.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def services(request):
    return render(request, 'services.html')

def programming(request):
    return render(request, 'programming.html')

def Design(request):
    return render(request, 'Design.html')

def Music(request):
    return render(request, 'music.html')

def Lang(request):
    return render(request, 'Lang.html')

def cooking(request):
    return render(request, 'cooking.html')

def business(request):
    return render(request, 'business.html')

def dancing(request):
    return render(request, 'dancing.html')

def register(request):
    return render(request, 'register.html')


# ==========================================================
# LOGOUT
# ==========================================================
def logout_user(request):
    logout(request)
    return redirect('/login/')


# ==========================================================
# WALLET (Advanced Credit Summary + History + Sessions)
# ==========================================================
@login_required
def wallet(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    now = timezone.now()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_week = start_today - timedelta(days=7)

    # Earned = hosting sessions
    earned_qs = LiveSession.objects.filter(host=user)

    # Spent = joining sessions
    spent_qs = SessionAttendance.objects.filter(attendee=user)

    # Summary calculations
    summary = {
        "earned": {
            "today": earned_qs.filter(scheduled_at__gte=start_today)
                              .aggregate(total=Sum("credit_reward"))["total"] or 0,
            "week": earned_qs.filter(scheduled_at__gte=start_week)
                             .aggregate(total=Sum("credit_reward"))["total"] or 0,
            "total": earned_qs.aggregate(total=Sum("credit_reward"))["total"] or 0,
        },
        "spent": {
            "today": spent_qs.filter(session__scheduled_at__gte=start_today)
                             .aggregate(total=Sum("credit_cost"))["total"] or 0,
            "week": spent_qs.filter(session__scheduled_at__gte=start_week)
                            .aggregate(total=Sum("credit_cost"))["total"] or 0,
            "total": spent_qs.aggregate(total=Sum("credit_cost"))["total"] or 0,
        },
    }

    # Combined transaction history
    history = []
    for s in earned_qs:
        history.append({
            "title": s.title,
            "type": "earned",
            "credits": s.credit_reward,
            "dt": s.scheduled_at,
        })

    for a in spent_qs.select_related("session"):
        history.append({
            "title": a.session.title,
            "type": "spent",
            "credits": a.credit_cost,
            "dt": a.session.scheduled_at,
        })

    history.sort(key=lambda x: x["dt"], reverse=True)

    # Upcoming / Past sessions
    upcoming_host = earned_qs.filter(scheduled_at__gte=now).order_by("scheduled_at")[:5]
    upcoming_attend = spent_qs.filter(session__scheduled_at__gte=now)\
                              .select_related("session").order_by("session__scheduled_at")[:5]

    past_host = earned_qs.filter(scheduled_at__lt=now).order_by("-scheduled_at")[:5]
    past_attend = spent_qs.filter(session__scheduled_at__lt=now)\
                          .select_related("session").order_by("-session__scheduled_at")[:5]

    context = {
        "profile": profile,
        "summary": summary,
        "history": history,
        "upcoming_host": upcoming_host,
        "upcoming_attend": upcoming_attend,
        "past_host": past_host,
        "past_attend": past_attend,
    }

    return render(request, "wallet.html", context)


# ==========================================================
# HOST A LIVE SESSION
# ==========================================================
@login_required
def host_session(request):
    if request.method == "POST":
        title = request.POST.get("title")
        schedule = request.POST.get("schedule")

        session = LiveSession.objects.create(
            host=request.user,
            title=title,
            scheduled_at=schedule,
            credit_reward=10,
        )

        profile = request.user.profile
        profile.credits += session.credit_reward
        profile.save()

        return redirect("wallet")

    return render(request, "host_session.html")


# ==========================================================
# JOIN A LIVE SESSION
# ==========================================================
@login_required
def join_session(request, session_id):
    session = LiveSession.objects.get(id=session_id)
    user = request.user

    attendance, created = SessionAttendance.objects.get_or_create(
        session=session,
        attendee=user,
        defaults={"credit_cost": 2}
    )

    if created:
        profile = user.profile
        profile.credits -= attendance.credit_cost
        profile.save()

    return redirect("wallet")


# ==========================================================
# SESSION LIST
# ==========================================================
def session_list(request):
    sessions = LiveSession.objects.all().order_by("scheduled_at")
    return render(request, "session_list.html", {"sessions": sessions})

def browse_sessions(request):
    sessions = LiveSession.objects.all().order_by("scheduled_at")
    return render(request, "browse_sessions.html", {"sessions": sessions})
