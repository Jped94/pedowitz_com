from django import forms

class DatasetDateForm(forms.Form):
    from_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
