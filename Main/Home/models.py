from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==========================================================
# USER PROFILE (Credits System)
# ==========================================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.credits} credits"


# ==========================================================
# LIVE SESSION MODEL (Main Teaching System)
# ==========================================================
class LiveSession(models.Model):
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hosted_sessions"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)

    credit_reward = models.IntegerField(default=10)  # Credits teacher earns
    max_attendees = models.PositiveIntegerField(null=True, blank=True)

    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.host.username}"

    @property
    def attendee_count(self):
        return self.attendances.count()

# ==========================================================
# SESSION ATTENDANCE (When a student joins a session)
# ==========================================================
class SessionAttendance(models.Model):
    session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    attendee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attended_sessions"
    )

    credit_cost = models.IntegerField(default=2)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "attendee")  # 1 user cannot join twice

    def __str__(self):
        return f"{self.attendee.username} attended {self.session.title}"


# ==========================================================
# AUTO CREATE PROFILE WHEN USER IS CREATED
# ========================================================== 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
