from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import os


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('investigator', 'Investigator'),
        ('legal', 'Legal Officer'),
        ('analyst', 'Analyst'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='investigator')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Case(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_cases')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


def evidence_upload_path(instance, filename):
    return f"evidence/case_{instance.case.id}/{filename}"


class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='evidence')
    file = models.FileField(upload_to=evidence_upload_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.filename()


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('create_case', 'Created Case'),
        ('update_case', 'Updated Case'),
        ('upload_evidence', 'Uploaded Evidence'),
        ('change_status', 'Changed Case Status'),
        ('add_comment', 'Added Comment'),
        ('add_suspect', 'Added Suspect'),
        ('add_deadline', 'Added Deadline'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} on {self.case.title}"


class CaseStatusLog(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='status_logs')
    previous_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.case.title}: {self.previous_status} → {self.new_status} by {self.changed_by}"


# ── NEW FEATURES ──────────────────────────────────────────────────────────────

class CaseComment(models.Model):
    """Investigators/legal can leave notes on a case."""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.case.title}"


class Suspect(models.Model):
    """Person of interest linked to one or more cases."""
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='suspects')
    full_name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='suspects/', blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class CaseDeadline(models.Model):
    """Court dates and important deadlines per case."""
    DEADLINE_TYPE_CHOICES = (
        ('court_date', 'Court Date'),
        ('filing', 'Filing Deadline'),
        ('hearing', 'Hearing'),
        ('review', 'Case Review'),
        ('other', 'Other'),
    )

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='deadlines')
    title = models.CharField(max_length=255)
    deadline_type = models.CharField(max_length=20, choices=DEADLINE_TYPE_CHOICES, default='other')
    due_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['due_date']

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.now()

    def __str__(self):
        return f"{self.title} — {self.case.title} ({self.due_date.date()})"


class Notification(models.Model):
    """In-app notifications for users."""
    NOTIF_TYPE_CHOICES = (
        ('case_assigned', 'Case Assigned'),
        ('status_changed', 'Status Changed'),
        ('comment_added', 'Comment Added'),
        ('deadline_due', 'Deadline Due'),
        ('evidence_uploaded', 'Evidence Uploaded'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPE_CHOICES)
    message = models.TextField()
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message[:50]}"
