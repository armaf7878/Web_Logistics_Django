from django.db import models
from django import forms
# Create your models here.
class ProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    supplier = forms.CharField(max_length=100)
    quantity = forms.IntegerField()
    category = forms.CharField(max_length=50)
    unit = forms.CharField(max_length=20)
    warehouse_location = forms.CharField(max_length=50)
