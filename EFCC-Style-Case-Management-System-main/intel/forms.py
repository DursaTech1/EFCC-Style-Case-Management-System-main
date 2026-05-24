from django import forms
from .models import IntelligenceSource, IntelReport
from taggit.forms import TagWidget


class IntelligenceSourceForm(forms.ModelForm):
    class Meta:
        model = IntelligenceSource
        fields = ['name', 'source_type', 'contact_info', 'reliability_score', 'notes', 'tags']
        widgets = {
            'tags': TagWidget(),
        }


class IntelReportForm(forms.ModelForm):
    class Meta:
        model = IntelReport
        fields = ['case', 'title', 'content', 'report_type', 'status', 'source', 'tags', 'latitude', 'longitude']
        widgets = {
            'tags': TagWidget(),
        }
