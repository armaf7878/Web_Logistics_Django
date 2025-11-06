from django.db import models
from django import forms
# Create your models here.
class ExportsForm(forms.Form):
    customer_name = forms.CharField(max_length=100)
    customer_phone = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    pickup_time = forms.DateTimeField(label ="pickup_time")
