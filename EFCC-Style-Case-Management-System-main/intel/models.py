from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model
from core.models import Case


# Create your models here.
User = get_user_model()

class IntelligenceSource(models.Model):
    SOURCE_TYPES = [
        ('human', 'Human Intelligence'),
        ('signal', 'Signal Intelligence'),
        ('open', 'Open Source'),
        ('cyber', 'Cyber Intelligence'),
    ]

    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    contact_info = models.TextField(blank=True)
    reliability_score = models.IntegerField(default=3)  # 1–5
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class IntelReport(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='intel_reports')
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.ForeignKey(IntelligenceSource, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title

