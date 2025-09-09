# designer/forms.py
from django import forms
from .models import AbayaDesign

class DesignForm(forms.ModelForm):
    class Meta:
        model = AbayaDesign
        fields = ['style', 'length', 'fabric', 'color']
