from django import forms
from .models import IntelligenceSource, IntelReport
from taggit.forms import TagWidget

class IntelligenceSourceForm(forms.ModelForm):
    class Meta:
        model = IntelligenceSource
        fields = ['name', 'source_type', 'contact_info', 'reliability_score', 'notes']


class IntelReportForm(forms.ModelForm):
    class Meta:
        model = IntelReport
        fields = ['title', 'content', 'tags', 'source']



class IntelligenceReportForm(forms.ModelForm):
    class Meta:
        model = IntelReport
        fields = ['title', 'content', 'source', 'tags']
        widgets = {
            'tags': TagWidget()
        }
