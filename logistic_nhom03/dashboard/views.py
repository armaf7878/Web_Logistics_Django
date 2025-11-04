from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
from django.http import JsonResponse
import requests 
import json 

def dashboard(request):
    firebase_user = request.session.get('firebase_user')
    if not firebase_user:
        return redirect('login')
    name = firebase_user.get('displayName')  
    context= {
        'name': name
    } 
    return render(request ,'dashboard/dashboard.html', context)
  
    